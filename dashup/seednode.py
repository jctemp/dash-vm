import shutil
import dashup.helper.utils as utils
import dashup.helper.rpc as rpc
import json
import time
import os
import re


def setup() -> None:
    '''
    Setup platform wallets
    '''
    utils.hline()
    utils.title("Seednode setup")
    utils.info("Setting up seednode")
    try:
        local_settings = {"wallet": "", "address": "",
                          "port": "", "username": "", "password": ""}

        rpc.stop(local_settings)
        time.sleep(2)
        rpc.start()
        rpc.sync(local_settings)
        rpc.test(local_settings)

        sporks = generate_spork(local_settings.copy())
        write_json(sporks, "sporks.json")

        platform_wallets = generate_platform_wallets(local_settings.copy())
        write_json(platform_wallets, "platform_wallets.json")

        shutil.copy("platform_wallets.json", "/vagrant")

        tempalte_file = "/vagrant/template.dash.conf"
        if not os.path.isfile(tempalte_file):
            raise Exception("Template file not found")

        local_conf = os.path.expanduser("~/.dashcore/dash.conf")
        if not os.path.isfile(local_conf):
            raise Exception("Local dash.conf not found")

        utils.replace_in_file(tempalte_file, r"^(# |)sporkaddr=(\w+|)$",
                              "sporkaddr={}".format(sporks["address"]))

        utils.replace_in_file(local_conf, r"^(# |)sporkaddr=(\w+|)$",
                              "sporkaddr={}".format(sporks["address"]))

        utils.replace_in_file(local_conf, r"^(# |)sporkkey=(\w+|)$",
                              "sporkkey={}".format(sporks["key"]))

        print("How many masternodes do you want to create?")
        mn_count = int(utils.get_input("Count: ", utils.re_template.NUMBERS))
        required_funds = 1005 * mn_count

        while required_funds > rpc.get_balance(local_settings):
            rpc.generate_blocks(1, local_settings)

        utils.append_to_crontab(
            "*/3 * * * * pgrep dashd && \
            /usr/local/bin/dash-cli generate 1 >> ~/.dashcore/generated-blocks.log")

        rpc.stop(local_settings)
        time.sleep(2)
        rpc.start()
        rpc.sync(local_settings)
    except rpc.RPCException as e:
        utils.error(e.response)
        utils.hline()
        exit(1)
    except Exception as e:
        utils.error("Setup failed")
        utils.hline()
        e.with_traceback()
        exit(1)
    utils.success("Setup complete")
    utils.hline()


def generate_spork(rpcsettings: dict = None) -> dict:
    '''
    Generate spork address and key
    @param rpcsettings: rpc settings to use
    '''
    utils.info("Generating sporks")

    # create spork wallet
    if not rpc.exist_wallet(r"spork") and not rpc.create_wallet(r"spork"):
        raise Exception("Failed to create spork wallet")

    rpcsettings["wallet"] = r"spork"
    settings = rpc.check_rpcsettings(rpcsettings)

    # the get new address is the public address for spork
    address = rpc.new_address(rpcsettings)

    # with dumpprivkey one retrieves the private key corresponding to the address
    response = rpc.rpc(settings["url"], "dumpprivkey", [address],
                       settings["username"], settings["password"])

    rpc.unload_wallet(r"spork", rpcsettings)

    return {"address": address, "key": response[r"result"]}


def generate_platform_wallets(rpcsettings: dict = None) -> dict:
    '''
    Generate HD wallets
    @param rpcsettings: rpc settings to use
    '''
    utils.info("Generating platform keys")

    names = ["dpns", "dashpay", "feature_flags", "masternode_reward_shares"]
    wallets = {}
    for name in names:
        # create wallet
        if not rpc.exist_wallet(name) and not rpc.create_wallet(name):
            raise Exception("Failed to create spork wallet")

        # set wallet url
        wallet_settings = {
            "wallet": name,
            "address": rpcsettings["address"],
            "port": rpcsettings["port"],
            "username": rpcsettings["username"],
            "password": rpcsettings["password"]
        }

        settings = rpc.check_rpcsettings(wallet_settings)

        # upgrade to hdwallet
        if not rpc.hd_wallet(wallet_settings):
            rpc.upgrade_wallet(wallet_settings)

        # create derived key
        address = rpc.new_address(wallet_settings)
        response = rpc.rpc(settings["url"], "dumpprivkey", [address],
                           settings["username"], settings["password"])
        derived_priv_key = response[r"result"]
        response = rpc.rpc(settings["url"], "getaddressinfo", [
                           address], settings["username"], settings["password"])
        derived_pub_key = response[r"result"]["pubkey"]

        # dumpwallet to file
        if os.path.exists(name):
            utils.remove(name)

        response = rpc.rpc(settings["url"], "dumpwallet", [
            name], settings["username"], settings["password"])

        rpc.unload_wallet(name, rpcsettings)

        # find path to file to get platform keys
        path = ""
        if not "result" in response or response["result"] == None:
            try:
                path = re.search(
                    "(\/\w+)+", response["error"]["message"]).group(0)
            except AttributeError:
                raise Exception("File to key dump not found")
        else:
            path = response["result"]["filename"]

        # check file
        if not os.path.isfile(path):
            raise Exception("File to key dump not found")

        # extracting keys from file
        data = []
        with open(path, "r") as f:
            data = f.readlines()

        for line in data:
            if "extended private masterkey:" in line:
                private_masterkey = line.split(":")[1].strip()
            elif "extended public masterkey:" in line:
                public_masterkey = line.split(":")[1].strip()

        wallets[name] = {"private_masterkey": private_masterkey,
                         "public_masterkey": public_masterkey,
                         "derived_priv_key": derived_priv_key,
                         "derived_pub_key": derived_pub_key}
    return wallets


def write_json(data: dict, filename: str) -> None:
    '''
    Write json to file
    @param data: data to write
    @param filename: filename to write to
    '''
    utils.info(f"Writing {filename}")
    with open(filename, "w") as f:
        f.write(json.dumps(data, indent=4))
