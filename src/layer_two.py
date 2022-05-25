#!/usr/bin/python3

import rpc

def exist_wallet(client: rpc.Client, name: str) -> bool:
    
    # contained in the list of wallets
    data = rpc.unpack_response(client.request("listwallets"))
    if (name in data):
        return True
    
    # load wallet
    data = rpc.unpack_response(client.request("loadwallet", [name]), False)
    if ("name" in data):
        return True
    
    # not loadable
    return False

def generate_spork(client: rpc.Client):
    wallet = r"spork"
    
    if not exist_wallet(client, wallet):
        client.request("createwallet", [wallet], wallet)
        
    address = rpc.unpack_response(client.request("getnewaddress", [], wallet))
    key = rpc.unpack_response(client.request("dumpprivkey", [address], wallet))
    
    return address, key

client = rpc.Client()
print(generate_spork(client))
    