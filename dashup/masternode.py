import dashup.helper.utils as utils
import dashup.helper.rpc as rpc
import json
import time
import os
import re

# TODO: wait for node to run
# TODO: restart node


def setup() -> None:
    '''
    Setup dash node to become masternode
    '''
    utils.hline()
    utils.title("Masternode setup")
    utils.info("Setting up masternode")

    try:
        local_settings = {"wallet": "", "address": "",
                          "port": "", "username": "", "password": ""}

        rpc.stop(local_settings)
        time.sleep(2)
        rpc.start()
        rpc.sync(local_settings)
        rpc.test()

        extern_settings = {"wallet": "", "address": "10.0.0.10",
                           "port": 19998, "username": "", "password": ""}

        rpc.sync(local_settings)

        collateral_data = collateral(local_settings, extern_settings)
        bls_data = bls(local_settings)
        address_data = generate_addresses(local_settings, extern_settings)
        config_data = load_config()
        protx_data = protx(local_settings, collateral_data, bls_data,
                           address_data, config_data)
        wait_for_masternode(local_settings,
                            extern_settings, protx_data["hash"])
        set_bls_key(bls_data["secret"])
        dump_info(collateral_data, bls_data,
                  address_data, config_data, protx_data)

        install_sentinel("/vagrant/downloads.json")

        rpc.stop(local_settings)
        time.sleep(2)
        rpc.start()
        rpc.sync(local_settings)

    except rpc.RPCException as e:
        utils.error("Setup failed: ")
        utils.error(e.response)
        utils.hline()
        e.with_traceback()
        exit(1)

    except Exception as e:
        utils.error("Setup failed")
        utils.hline()
        e.with_traceback()
        exit(1)

    utils.success("Setup complete")
    utils.hline()


def collateral(local: dict, extern: dict) -> dict:

    utils.info("Creating collateral")

    # create local address
    address = rpc.new_address(local)

    # fund address by external
    hash = rpc.send_funds(address=address, amount=1000, rpcsettings=extern)

    # check if transaction is confirmed
    while not rpc.is_confirmed(hash, 1, extern):
        rpc.generate_blocks(1, extern)
        time.sleep(.2)

    vout = rpc.txout(address=address, hash=hash, rpcsettings=local)

    return {
        "address": address,
        "hash": hash,
        "vout": vout
    }


def bls(local: dict) -> dict:

    utils.info("Generating bls key")

    settings = rpc.check_rpcsettings(local)
    response = rpc.rpc(settings["url"], "bls",
                       ["generate"], settings["username"], settings["password"])
    return response["result"]


def generate_addresses(local: dict, extern: dict) -> dict:
    utils.info("Generating and funding addresses")

    owner = rpc.new_address(local)
    voting = rpc.new_address(local)
    payout = rpc.new_address(local)
    fee_source = rpc.new_address(local)

    # fund payout and fee_source
    hash = rpc.send_funds(payout, 1, extern)

    while not rpc.is_confirmed(hash, 1, extern):
        rpc.generate_blocks(1, extern)
        time.sleep(.2)

    hash = rpc.send_funds(fee_source, 1, extern)

    while not rpc.is_confirmed(hash, 1, extern):
        rpc.generate_blocks(1, extern)
        time.sleep(.2)

    return {
        "owner": owner,
        "voting": voting,
        "payout": payout,
        "fee_source": fee_source
    }


def load_config() -> dict:
    utils.info("Retrieving config of machine")

    config = os.path.expanduser(r"~/.dashcore/dash.conf")
    with open(config, "r") as f:
        content = f.read()

    # get external ip
    match = re.search(r"externalip=(\d|\.)+", content)
    external_ip = match.group(0).split("=")[1]

    # get p2p port
    match = re.search(r"port=(\d|\.)+", content)
    p2p_port = match.group(0).split("=")[1]

    return {
        "external_ip": external_ip,
        "p2p_port": p2p_port
    }


def protx(local: dict, collateral_data, bls_data, address_data, config_data) -> None:
    utils.info("ProTx registration")

    local_settings = rpc.check_rpcsettings(local)
    try:
        # prepare protx data
        method = "protx"
        params = ["register_prepare", collateral_data["hash"], collateral_data["vout"],
                  config_data["external_ip"] + ":" +
                  str(config_data["p2p_port"]),
                  address_data["owner"], bls_data["public"], address_data["voting"], 0,
                  address_data["payout"], address_data["fee_source"]]

        response = rpc.rpc(local_settings["url"], method, params,
                           local_settings["username"], local_settings["password"])
        result = response["result"]

        signmessage = result["signMessage"]
        tx = result["tx"]

        # sign protx message
        method = "signmessage"
        params = [collateral_data["address"], signmessage]
        response = rpc.rpc(local_settings["url"], method, params,
                           local_settings["username"], local_settings["password"])
        signature = response["result"]

        # submit protx
        method = "protx"
        params = ["register_submit", tx, signature]

        hash = rpc.rpc(local_settings["url"], method, params,
                       local_settings["username"], local_settings["password"])["result"]

    except rpc.RPCException as e:
        print(json.dumps(e.response, indent=4))
        exit(1)

    return {
        "signature": signature,
        "hash": hash
    }


def wait_for_masternode(local: dict, extern: dict, protx_hash: str) -> None:
    utils.info("Waiting for node to appear in masternode list")

    settings = rpc.check_rpcsettings(local)
    method = "masternode"
    params = ["list"]

    # wait for masternode to be registered
    while True:
        rpc.sync(local)
        response = rpc.rpc(settings["url"], method, params,
                           settings["username"], settings["password"])
        result = response["result"]

        for entry in result:
            if result[entry]["proTxHash"] == protx_hash:
                return
        rpc.generate_blocks(1, extern)


def set_bls_key(op_priv_key: str) -> None:
    utils.info("Set bls key in config")
    local_conf = os.path.expanduser("~/.dashcore/dash.conf")
    if not os.path.isfile(local_conf):
        raise Exception("Local dash.conf not found")

    utils.replace_in_file(local_conf, r"^(# |)masternodeblsprivkey=(\w+|)$",
                          "masternodeblsprivkey={}".format(op_priv_key))


def dump_info(collateral_data: dict, bls_data: dict, address_data: dict,
              config_data: dict, protx_data: dict) -> None:

    json_data = {
        "collateral": collateral_data,
        "bls": bls_data,
        "address": address_data,
        "config": config_data,
        "protx": protx_data
    }

    # (over)-write to masternode.json file
    masternode_json = os.path.expanduser("~/masternode.json")
    with open(masternode_json, "w") as f:
        f.write(json.dumps(json_data, indent=4))


def install_sentinel(downloads: str):
    utils.info("Installing sentinel")

    os.chdir(os.path.expanduser("~"))

    if not os.path.exists(downloads) or not os.path.isfile(downloads):
        raise Exception("downloads.json not found")

    with open(downloads, "r") as f:
        content = f.read()
    json_data = json.loads(content)

    if not "sentienl" in json_data:
        raise Exception("sentienl not found in downloads.json")

    url = json_data["sentienl"]["url"]
    branch = json_data["sentienl"]["branch"]

    utils.clone_repository(url, "sentinel", branch)
    os.chdir("sentinel")

    result = utils.execute_process("virtualenv venv >env-debug.log")
    if not result["status"]:
        raise Exception("Failed to create virtualenv")

    result = utils.execute_process(
        "venv/bin/pip install -r requirements.txt >env-debug.log")
    if not result["status"]:
        raise Exception("Failed to install requirements")

    utils.append_to_crontab(
        "* * * * * cd ~/sentinel && venv/bin/python bin/sentinel.py 2>&1 >> ~/sentinel/sentinel-cron.log")

