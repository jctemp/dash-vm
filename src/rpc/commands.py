from src.rpc.packing import pack_request, unpack_response
from src.rpc.client import Client


def exist_wallet(c: Client, name: str) -> bool:
    # contained in the list of wallets
    data = unpack_response(c.request(pack_request("listwallets", [])))
    if (name in data):
        return True

    # load wallet
    data = unpack_response(c.request(pack_request("loadwallet", [name])), False)
    if ("name" in data):
        return True

    # not loadable
    return False


def generate_spork(c: Client):
    wallet = r"spork"

    if not exist_wallet(c, wallet):
        c.request(pack_request("createwallet", [wallet]), wallet)

    address = unpack_response(c.request(pack_request("getnewaddress", []), wallet))
    key = unpack_response(c.request(pack_request("dumpprivkey", [address]), wallet))

    return address, key


def generate_platform_keys(c: Client):
    wallet = r"platform"

    if not exist_wallet(c, wallet):
        c.request(pack_request("createwallet", [wallet]), wallet)

    address = unpack_response(c.request(pack_request("getnewaddress", []), wallet))
    key = unpack_response(c.request(pack_request("dumpprivkey", [address]), wallet))

    return address, key

print(generate_spork(Client()))
