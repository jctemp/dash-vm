import dashup.helper.utils as utils
import dashup.helper.rpc as rpc
import time
import json
import toml
import re
import os


def setup() -> None:

    rpcsettings = {"wallet": "", "address": "localhost",
                   "port": 19998, "username": "dashrpc", "password": "password"}

    try:
        # install_mongod()
        platform_settings = generate_platform_settings(rpcsettings)
        install_tenderdash("/vagrant/downloads.json", platform_settings)
        # get_platform("/vagrant/downloads.json")
        install_drive(platform_settings)
        install_dapi(platform_settings)
        # # TODO: envoy https://www.envoyproxy.io/docs/envoy/latest/start/install
    except rpc.RPCException as e:
        utils.error(e.response)
        utils.hline()
        exit(1)
    except Exception as e:
        utils.error("Setup failed")
        utils.error(e)
        utils.hline()
        exit(1)

    utils.success("Setup complete")
    utils.hline()


def generate_platform_settings(rpcsettings: dict = None) -> dict:
    '''
    Generate platform settings
    '''
    settings = rpc.check_rpcsettings(rpcsettings)

    data = {
        "p2p_port": 0,
        "rpc_port": rpcsettings["port"],
        "rpc_user": rpcsettings["username"],
        "rpc_password": rpcsettings["password"],
        "quorum_type": "101",
        "chainlock_height": 0,
        "network_name": ""
    }

    config = os.path.expanduser(r"~/.dashcore/dash.conf")
    with open(config, "r") as f:
        content = f.read()

    match = re.search(r"port=(\d)+", content)
    p2p_port = match.group(0).split("=")[1]
    data["p2p_port"] = p2p_port

    response = rpc.rpc(settings["url"], "getbestchainlock", [],
                       settings["username"], settings["password"])
    data["chainlock_height"] = response["result"]["height"]

    response = rpc.rpc(settings["url"], "getblockchaininfo", [],
                       settings["username"], settings["password"])
    data["network_name"] = response["result"]["chain"]

    return data


def install_mongod() -> None:
    utils.info("Installing mongodb")
    if utils.execute_process("command -v mongod > /dev/null")["status"]:
        return

    utils.execute_process("sudo apt remove -y mongo*")
    utils.execute_process(
        "sudo rm -f /etc/apt/sources.list.d/mongodb-org-5.0.list")
    utils.execute_process(
        "wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -")
    utils.execute_process('echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" \
            | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list')
    utils.execute_process("sudo apt-get update")
    utils.execute_process("sudo apt-get install -y mongodb-org")
    utils.execute_process(
        "sudo sed -i 's/#replication:/replication:\n  replSetName: driveDocuments/' /etc/mongod.conf")
    utils.execute_process("sudo systemctl enable mongod")
    utils.execute_process("sudo systemctl restart mongod")
    while not utils.execute_process("pgrep mongod"):
        time.sleep(2)
    time.sleep(2)
    utils.execute_process(
        '''mongo<<<"rs.initiate({_id:'driveDocuments',version: 1,members:[{_id: 0,host: 'localhost:27017',},],});"''')


def install_tenderdash(downloads: str, platform_settings) -> None:
    '''
    Install tenderdash
    '''
    utils.info("Installing tenderdash")
    os.chdir(os.path.expanduser("~"))
    if not os.path.exists(os.path.expanduser(r"~/tenderdash")):

        if not os.path.exists(downloads) or not os.path.isfile(downloads):
            raise Exception("downloads.json not found")

        with open(downloads, "r") as f:
            downloads_json = json.load(f)

        if "tenderdash" not in downloads_json:
            raise Exception("tenderdash not found in downloads.json")

        tenderdash = downloads_json["tenderdash"]
        url = tenderdash["url"]
        branch = tenderdash["branch"]

        os.chdir(os.path.expanduser("~"))

        utils.clone_repository(url, "tenderdash", branch)

    if not utils.execute_process("command -v tenderdash > /dev/null")["status"]:

        os.chdir(os.path.expanduser(r"~/tenderdash"))

        result = utils.execute_process(
            "make install-bls > ./install-bls.log")
        if not result["status"]:
            raise Exception("Failed to execute make install-bls")

        result = utils.execute_process(
            "make build-linux > ./build-linux.log")
        if not result["status"]:
            raise Exception("Failed to execute make build-linux")

        if not utils.install_from_directory("build", "/usr/local/bin"):
            raise Exception("Failed to install tenderdash")

        os.chdir(os.path.expanduser("~"))

    if not os.path.exists(os.path.expanduser(r"~/.tenderdash")):

        utils.execute_process("tenderdash init > ./tenderdash-init.log")

        # edit config files
        with open(os.path.expanduser("~/.tenderdash/config/genesis.json"), "r") as f:
            genesis = json.load(f)

        config = toml.load(os.path.expanduser(
            "~/.tenderdash/config/config.toml"))

        # configure tenderdash: general
        config["moniker"] = "#\1"
        config["timeout_commit"] = "500ms"
        config["create_empty_blocks_interval"] = "3m"
        config["namespace"] = "drive_tendermint"
        config["priv_validator_core_rpc_host"] = f"127.0.0.1:{platform_settings['rpc_port']}"
        config["priv_validator_core_rpc_username"] = f"{platform_settings['rpc_user']}"
        config["priv_validator_core_rpc_password"] = f"{platform_settings['rpc_password']}"

        # configure tenderdash: local networks
        config["addr_book_strict"] = "false"
        config["quorum_type"] = str(platform_settings['quorum_type'])

        # configure tenderdash: genesis.json
        genesis["chain_id"] = platform_settings["network_name"]
        genesis["initial_core_chain_locked_height"] = platform_settings["chainlock_height"]
        genesis["quorum_type"] = str(platform_settings["quorum_type"])

        with open(os.path.expanduser("~/.tenderdash/config/genesis.json"), "w") as f:
            json.dump(genesis, f, indent=4)

        with open(os.path.expanduser("~/.tenderdash/config/config.toml"), "w") as f:
            toml.dump(config, f)


def get_platform(downloads: str):
    os.chdir(os.path.expanduser("~"))
    if not os.path.exists(os.path.expanduser(r"~/platform")):

        if not os.path.exists(downloads) or not os.path.isfile(downloads):
            raise Exception("downloads.json not found")

        with open(downloads, "r") as f:
            downloads_json = json.load(f)

        if "platform" not in downloads_json:
            raise Exception("platform not found in downloads.json")

        platform = downloads_json["platform"]
        url = platform["url"]
        branch = platform["branch"]

        os.chdir(os.path.expanduser("~"))

        utils.clone_repository(url, "platform", branch)

        os.chdir(os.path.expanduser("~/platform"))

        utils.execute_process("sudo corepack enable")


def install_drive(platform_settings: dict) -> None:
    '''
    Install javascript services
    '''
    utils.info("Installing drive services")

    os.chdir(os.path.expanduser("~/platform/packages/js-drive"))

    if not os.path.exists(".env"):

        utils.execute_process("cp .env.example .env")

        utils.replace_in_file(".env", r'^CORE_JSON_RPC_PORT.*',
                              f'CORE_JSON_RPC_PORT={platform_settings["rpc_port"]}')
        utils.replace_in_file(".env", r'^CORE_JSON_RPC_USERNAME.*',
                              f'CORE_JSON_RPC_USERNAME={platform_settings["rpc_user"]}')
        utils.replace_in_file(".env", r'^CORE_JSON_RPC_PASSWORD.*',
                              f'CORE_JSON_RPC_PASSWORD={platform_settings["rpc_password"]}')
        utils.replace_in_file(".env", r'^INITIAL_CORE_CHAINLOCKED_HEIGHT.*',
                              f'INITIAL_CORE_CHAINLOCKED_HEIGHT={platform_settings["chainlock_height"]}')
        utils.replace_in_file(".env", r'^VALIDATOR_SET_LLMQ_TYPE.*',
                              f'VALIDATOR_SET_LLMQ_TYPE={platform_settings["quorum_type"]}')
        utils.replace_in_file(".env", r'^NETWORK.*',
                              f'NETWORK={platform_settings["network_name"]}')

        with open("/vagrant/platform_wallets.json", "r") as f:
            wallets = json.load(f)

        for wallet in wallets:
            name = str(wallet).upper()
            utils.replace_in_file(".env", r'^{}_MASTER_PUBLIC_KEY=.*'.format(name),
                                  f'{name}_MASTER_PUBLIC_KEY={wallets[wallet]["derived_pub_key"]}')

        utils.execute_process("export npm_config_zmq_external=true")
        utils.execute_process("yarn install > ./yarn.log")


def install_dapi(platform_settings: dict) -> None:
    utils.info("Installing dapi services")

    os.chdir(os.path.expanduser("~/platform/packages/dapi"))

    if not os.path.exists(".env"):

        utils.execute_process("cp .env.example .env")

        utils.replace_in_file(".env", r'^API_JSON_RPC_PORT.*',
                              'API_JSON_RPC_PORT = 3004')
        utils.replace_in_file(".env", r'^API_GRPC_PORT.*',
                              'API_GRPC_PORT = 3005')
        utils.replace_in_file(
            ".env", r'^TX_FILTER_STREAM_GRPC_PORT.*', 'TX_FILTER_STREAM_GRPC_PORT = 3006')

        utils.replace_in_file(".env", r'^DASHCORE_RPC_USER.*',
                              f'DASHCORE_RPC_USER = {platform_settings["rpc_user"]}')
        utils.replace_in_file(".env", r'^DASHCORE_RPC_PASS.*',
                              f'DASHCORE_RPC_PASS = {platform_settings["rpc_password"]}')
        utils.replace_in_file(".env", r'^DASHCORE_RPC_PORT.*',
                              f'DASHCORE_RPC_PORT = {platform_settings["rpc_port"]}')
        utils.replace_in_file(".env", r'^DASHCORE_ZMQ_PORT.*',
                              f'DASHCORE_ZMQ_PORT = 29998')
        utils.replace_in_file(".env", r'^DASHCORE_P2P_PORT.*',
                              f'DASHCORE_P2P_PORT = {platform_settings["p2p_port"]}')
        utils.replace_in_file(".env", r'^DASHCORE_P2P_NETWORK.*',
                              f'DASHCORE_P2P_NETWORK = {platform_settings["network_name"]}')
        utils.replace_in_file(".env", r'^NETWORK.*',
                              f'NETWORK = {platform_settings["network_name"]}')

        utils.execute_process("export npm_config_zmq_external=true")
        utils.execute_process("yarn install > ./yarn.log")
