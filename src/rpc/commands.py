from src.rpc.packing import pack_request, unpack_response
from src.rpc.client import Client


def exist_wallet(c: Client, name: str) -> bool:
    # contained in the list of wallets
    data = unpack_response(c.request(pack_request("listwallets")))
    if name in data:
        return True

    # load wallet
    data = unpack_response(c.request(pack_request("loadwallet", [name])), False)
    if "name" in data:
        return True

    # not loadable
    return False


def unload_wallets(c: Client) -> None:
    # 1. get all wallets in listwallets
    wallets = unpack_response(c.request(pack_request("listwallets")))

    # 2. unload all wallets
    for wallet in wallets:
        if wallet == "":
            continue
        c.request(pack_request("unloadwallet", [wallet]))


def generate_spork(c: Client) -> tuple:
    wallet = r"spork"
    unload_wallets(c)

    # 1. create wallet if it not exists (keep default wallet clean)
    if not exist_wallet(c, wallet):
        c.request(pack_request("createwallet", [wallet]), wallet)

    # 2. an address is the spork address and the private key is the spork private key
    address = unpack_response(c.request(pack_request("getnewaddress"), wallet))
    key = unpack_response(c.request(pack_request("dumpprivkey", [address]), wallet))

    # 3. unload wallet to allow normal rpc usage
    c.request(pack_request("unloadwallet", [wallet]))

    # 4. save address with key
    return address, key


def generate_platform_keys(c: Client) -> tuple:
    wallets = ["dpns", "dashpay", "feature_flags", "masternode_reward_shares"]
    platform_keys = {}
    unload_wallets(c)

    # 0. iterate over all wallets to create keys
    for wallet in wallets:

        # 1. create wallet if it not exists (keep default wallet clean)
        if not exist_wallet(c, wallet):
            c.request(pack_request("createwallet", [wallet]), wallet)

        # 2. generate platform keys => only derived public keys are important
        # one can get master private key from the wallet by dumping walletinfo
        address = unpack_response(c.request(pack_request("getnewaddress"), wallet))
        address_info = unpack_response(c.request(pack_request("getaddressinfo", [address]), wallet))
        derived_public_key = address_info["pubkey"]

        # 3. add to the dict
        platform_keys[wallet] = derived_public_key

        # 4. unload wallet to allow normal rpc usage
        c.request(pack_request("unloadwallet", [wallet]))

    return platform_keys, wallets


def generate_collateral(c: Client) -> tuple:
    wallet = r"funding"
    unload_wallets(c)

    # 1. create an address
    address = unpack_response(c.request(pack_request("getnewaddress")))

    # 2.1. create wallet if it not exists (keep default wallet clean)
    if not exist_wallet(c, wallet):
        c.request(pack_request("createwallet", [wallet]))

    # 2.2. generate blocks to get funds until there is 1000 Dash per masternode
    # need to be on a different wallet to ensure not weird transactions
    # set threshold to 1001 to cover tx fees
    while unpack_response(c.request(pack_request("getbalance"), wallet)) < 1001:
        c.request(pack_request("generate", [1]), wallet)

    # 3. send money to the address
    txid = unpack_response(c.request(pack_request("sendtoaddress", [address, 1000, "collateral"]), wallet))

    # 4. check if transaction is confirmed
    while unpack_response(c.request(pack_request("gettransaction", [txid]), wallet))["confirmations"] < 1:
        c.request(pack_request("generate", [1]), wallet)

    # 5. unload wallet to allow normal rpc usage
    c.request(pack_request("unloadwallet", [wallet]))

    # 6. save address with transaction hash
    return address, txid
