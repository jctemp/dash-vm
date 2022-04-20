import dashup.helper.utils as utils
import requests
import json
import time
import os


class RPCException(Exception):
    '''
    Exception for RPC
    '''
    # string, response

    def __init__(self, message, response):
        super().__init__(message)
        self.response = response


class ResponseError(Exception):
    '''
    Exception for response
    '''
    # string, response

    def __init__(self, message, response):
        super().__init__(message)
        self.response = response


def rpc(url: str, method: str, params: list, username: str, password: str) -> any:
    '''
    Send rpc request to url with method and params
    @param url: url to send request to
    @param method: method to call
    @param params: parameters to send with request
    @param username: username to authenticate with
    @param password: password to authenticate with
    '''
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.post(url, data=json.dumps(
        payload), headers=headers, auth=(username, password))

    if response.status_code != 200:
        raise RPCException(
            f'RPC request failed with status code {response.status_code}', response.text)

    result = response.json()

    if "error" in result and result["error"] != None:
        raise ResponseError(
            f'RPC request failed with error {result["error"]}', response.text)

    return result


def check_rpcsettings(rpcsettings: dict) -> dict:
    '''
    Check rpc settings
    @param rpcsettings: rpc settings to check

    example:
    {
        "wallet": "name",
        "address": "localhost",
        "port": 19998,
        "username": "dashrpc",
        "password": "password"
    }

    '''
    settings = {
        "url": "http://localhost:19998",
        "username": "dashrpc",
        "password": "password"
    }

    # return default settings if no settings are provided
    if rpcsettings == None:
        return settings

    # check if rpc settings are given
    name = ["wallet", "address", "port", "username", "password"]
    for n in name:
        if n not in rpcsettings:
            raise Exception(f"Missing {n} in rpc settings")

    # set values if specified
    if rpcsettings["address"] != "" and rpcsettings["port"] != "":
        settings["url"] = f"http://{rpcsettings['address']}:{str(rpcsettings['port'])}"

    if rpcsettings["username"] != "":
        settings["username"] = rpcsettings["username"]

    if rpcsettings["password"] != "":
        settings["password"] = rpcsettings["password"]

    if rpcsettings["wallet"] != "":
        settings["url"] += f'/wallet/{rpcsettings["wallet"]}'

    return settings


def test(rpcsettings: dict = None) -> None:
    '''
    Test rpc connection
    @param rpcsettings: rpc settings to use
    '''
    try:
        result = check_rpcsettings(rpcsettings)
        rpc(result["url"], "getmininginfo", [],
            result["username"], result["password"])
    except Exception as e:
        utils.error(f"RPC connection failed with error")
        exit(1)


def start() -> None:
    '''
    Start dashd
    @param rpcsettings: rpc settings to use
    '''
    if not utils.execute_process("pgrep dashd > /dev/null")["status"]:
        utils.execute_process("dashd > /dev/null")


def stop(rpcsettings: dict = None) -> None:
    '''
    Restart dashd
    @param rpcsettings: rpc settings to use
    '''
    if not utils.execute_process("pgrep dashd > /dev/null")["status"]:
        return

    settings = check_rpcsettings(rpcsettings)

    rpc(settings["url"], "stop", [],
        settings["username"], settings["password"])


def load_rpc_settings(path: str) -> dict:
    '''
    Load rpc settings from json file\n
    Expected format:
    {
        "wallet": "name",
        "address": "localhost",
        "port": "19998",
        "username": "dashrpc",
        "password": "password"
    }
    @param path: path to json file
    '''
    if not os.path.isfile(path):
        raise Exception(f"File {path} does not exist")

    with open(path, 'r') as f:
        settings = json.load(f)
    return settings


def generate_blocks(n: int, rpcsettings: dict = None) -> dict:
    '''
    Generate n blocks
    @param n: number of blocks to generate
    @param rpcsettings: rpc settings to use

    on success:
    {
        "hashes": [
            "<hash1>",
            ...,
            "<hashN>"
        ],
        "count": N
    }

    '''
    settings = check_rpcsettings(rpcsettings)

    got = 0
    required = n
    hashes = []
    while got < required:
        response = rpc(settings["url"], "generate", [
            n - got], settings["username"], settings["password"])

        got += len(response[r"result"])
        hashes.extend(response[r"result"])

    return {"hashes": hashes, "count": got}


def is_confirmed(txid: str, confirmations: int = 1, rpcsettings: dict = None) -> bool:
    '''
    Check if transaction is confirmed
    @param txid: transaction id
    @param confirmations: number of confirmations to check for
    @param rpcsettings: rpc settings to use

    {"success": True, "count": 0}

    '''
    settings = check_rpcsettings(rpcsettings)

    response = rpc(settings["url"], "gettransaction", [txid],
                   settings["username"], settings["password"])

    result = response[r"result"]
    if result["confirmations"] < confirmations:
        return False
    return True


def send_funds(address: str, amount: float, rpcsettings: dict = None) -> str:
    '''
    Send funds to address
    @param address: address to send funds to
    @param amount: amount to send
    @param rpcsettings: rpc settings to use
    '''
    settings = check_rpcsettings(rpcsettings)

    response = rpc(settings["url"], "sendtoaddress", [
        address, amount], settings["username"], settings["password"])

    return response[r"result"]


def new_address(rpcsettings: dict = None) -> str:
    '''
    Generate new address
    @param rpcsettings: rpc settings to use

    on success:
        "address": "<address>"
    '''
    settings = check_rpcsettings(rpcsettings)

    response = rpc(settings["url"], "getnewaddress",
                   [], settings["username"], settings["password"])

    return response[r"result"]


def exist_wallet(name: str, rpcsettings: dict = None) -> bool:
    '''
    Check if wallet exists
    @param name: wallet name
    @param rpcsettings: rpc settings to use

    on success:
        True
    '''
    settings = check_rpcsettings(rpcsettings)

    response = rpc(settings["url"], "listwallets", [],
                   settings["username"], settings["password"])

    result = response[r"result"]

    if name in result:
        return True

    try:
        response = rpc(settings["url"], "loadwallet", [name],
                       settings["username"], settings["password"])
    except:
        return False

    result = response[r"result"]

    return result["name"] == name


def create_wallet(name: str, rpcsettings: dict = None) -> bool:
    '''
    Create wallet
    @param name: wallet name
    @param rpcsettings: rpc settings to use
    '''
    settings = check_rpcsettings(rpcsettings)

    response = rpc(settings["url"], "createwallet", [name],
                   settings["username"], settings["password"])

    return response[r"result"]["name"] == name


def hd_wallet(rpcsettings: dict = None) -> str:
    '''
    Create HD wallet
    @param rpcsettings: rpc settings to use
    '''
    settings = check_rpcsettings(rpcsettings)

    response = rpc(settings["url"], "getwalletinfo", [],
                   settings["username"], settings["password"])

    if "hdaccountcount" in response[r"result"]:
        return True
    return False


def upgrade_wallet(rpcsettings: dict = None) -> any:
    '''
    Upgrade wallet
    @param name: wallet name
    @param rpcsettings: rpc settings to use
    '''
    settings = check_rpcsettings(rpcsettings)

    response = rpc(settings["url"], "upgradetohd", [],
                   settings["username"], settings["password"])

    return response[r"result"]


def unload_wallet(name: str, rpcsettings: dict = None) -> None:
    '''
    Unload wallet
    @param name: wallet name
    @param rpcsettings: rpc settings to use
    '''
    rpcsettings["wallet"] = ""
    settings = check_rpcsettings(rpcsettings)
    rpc(settings["url"], "unloadwallet", [name],
        settings["username"], settings["password"])


def sync(rpcsettings: dict = None) -> bool:
    '''
    Sync wallet
    @param rpcsettings: rpc settings to use
    '''
    settings = check_rpcsettings(rpcsettings)

    while not utils.execute_process("pgrep dashd > /dev/null")["status"]:
        time.sleep(1)
    time.sleep(2)

    # reset node sync to remove side effects
    rpc(settings["url"], "mnsync", ["reset"],
        settings["username"], settings["password"])

    # start sync as until finished
    while True:
        response = rpc(settings["url"], "mnsync", ["next"],
                       settings["username"], settings["password"])
        result = response[r"result"]

        if r"MASTERNODE_SYNC_FINISHED" in result:
            break

    return True


def get_balance(rpcsettings: dict = None) -> float:
    '''
    Get wallet balance
    @param rpcsettings: rpc settings to use

    on success:
        <balance>
    '''
    settings = check_rpcsettings(rpcsettings)

    response = rpc(settings["url"], "getwalletinfo", [],
                   settings["username"], settings["password"])

    return response[r"result"]["balance"]


def txout(address: str, hash: str, rpcsettings: dict = None) -> dict:
    '''
    Get transaction output
    @param address: address to get transaction output
    @param hash: transaction hash
    @param rpcsettings: rpc settings to use

    On success:
    {
        "status": true,
        "vout": <vout>
    }
    '''

    settings = check_rpcsettings(rpcsettings)

    count = 0
    while True:
        response = rpc(settings["url"], "gettxout", [hash, count],
                       settings["username"], settings["password"])

        result = response[r"result"]
        # tx output is not set for 0 sometimes => returns null
        if count == 10:
            raise Exception("Could not find transaction output")
        if result is None:
            continue
        if address in response["result"]["scriptPubKey"]["addresses"]:
            return count

        count += 1


def sporks(rpcsettings: dict = None) -> dict:
    settings = check_rpcsettings(rpcsettings)

    response = rpc(settings["url"], "spork", ["active"],
                   settings["username"], settings["password"])
    result = response[r"result"]

    return result


def quorum(rpcsettings: dict = None) -> dict:
    settings = check_rpcsettings(rpcsettings)

    response = rpc(settings["url"], "quorum", ["list"],
                   settings["username"], settings["password"])
    result = response[r"result"]

    return result


def chainlock(rpcsettings: dict = None) -> bool:
    settings = check_rpcsettings(rpcsettings)

    try:
        response = rpc(settings["url"], "getbestchainlock", [],
                       settings["username"], settings["password"])
    except:
        return False
    return True


rpcsettings = {"wallet": "", "address": "localhost",
               "port": 19998, "username": "dashrpc", "password": "password"}
# settings = check_rpcsettings(rpcsettings)

print(chainlock(rpcsettings))
# print(quorum(rpcsettings))

# print(sporks(rpcsettings))

# print(rpc(settings["url"], "gettxout", ["b622c08fc516f320c91f869fa52b18a36f7a12245eb7defa603c3579c9b383a1", 1], settings["username"], settings["password"]))


# print(is_confirmed(
#     "f98e7523eab526ffdccfa7a73db1ae06c0fe5dd339897c9756d42a0333a680b6", 1, rpcsetting))


# print(rpc(rpcsetting["address"] + ":" + str(rpcsetting["port"]),
#       "getmininginfo", [], rpcsetting["username"], rpcsetting["password"]))

# print(txout("yTUivTFsbxkjPvgegTibGa2NCvuuihg2Ky",
#       "a422d1fd6dab2b9a8ef3ee6774fcab3a5cfaf31f054782ff4693f61e1ba169ef", rpcsetting)
#       )


# rpcsetting["wallet"] = ""
# print(json.dumps(sync(rpcsetting), indent=4))


# rpcsetting["wallet"] = "faucet"
# print(json.dumps(generate_blocks(2, rpcsetting), indent=4))


# rpcsetting["wallet"] = "test"
# print(json.dumps(is_confirmed(
#     "72d0e8817d76ef48faff327850c5ca23eb9e8e6aba17948c66d868fa64744e0e", 2, rpcsetting), indent=4))


# rpcsetting["wallet"] = "faucet"
# print(json.dumps(send_funds("ySbqCKXiYrnuoGhGGK51Ggyr1Jxmehcipv", 1, rpcsetting), indent=4))


# rpcsetting["wallet"] = "test"
# print(json.dumps(new_address(rpcsetting), indent=4))


# print(json.dumps(create_wallet(str(random.random()),rpcsetting), indent=4))


# print(json.dumps(generate_spork(rpcsetting), indent=4))


# print(json.dumps(generate_platform_wallets(rpcsetting), indent=4))
