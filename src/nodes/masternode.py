import os.path
import json
import time

from rich.pretty import pprint
from rich.prompt import Prompt, Confirm

from src.rpc.client import Client
from src.rpc.commands import sync
from src.rpc.packing import unpack_response, pack_request
from src.utils import templater

from rich.progress import Console
from rich.traceback import install as install_traceback

from src.nodes.core import CoreData
from src.utils.command import command

install_traceback()


def masternode(data: CoreData):
    client = Client()

    sync(client)

    # 1. create or set masternode addresses
    collateral = {}
    if Confirm.ask("Load collaterals from file?"):
        with open(os.path.expanduser("./collateral.json"), "r") as f:
            collaterals = json.loads(f.read())
    else:
        collateral["address"] = Prompt.ask("collateral address")
        collateral["hash"] = Prompt.ask("collateral hash")
        collateral["key"] = Prompt.ask("collateral key")

    client.request(pack_request("importprivkey", [collateral["key"]]))

    # 1.1. find txout
    for i in range(100):
        vout = unpack_response(client.request(pack_request("gettxout", [collateral["hash"], i])))
        if vout is None:
            continue
        if "scriptPubKey" in vout:
            for address in vout["scriptPubKey"]["addresses"]:
                if address == collateral["address"]:
                    collateral["txout"] = i
                    break

    assert "txout" in collateral

    owner_address = unpack_response(client.request(pack_request("getnewaddress")))
    voting_address = unpack_response(client.request(pack_request("getnewaddress")))
    payout_address = unpack_response(client.request(pack_request("getnewaddress")))
    fee_address = unpack_response(client.request(pack_request("getnewaddress")))

    # 2. fund payout address
    Console().print("Send funds to {}".format(fee_address), style="bold cyan")
    Console().print("Waiting for funds...")
    while True:
        balance = unpack_response(client.request(pack_request("getaddressbalance", [fee_address])))["balance_spendable"]
        time.sleep(2)
        if balance > 0:
            break

    with Console().status("Prepare Masternode", spinner="arc") as console:
        # 3. generate bls data
        bls_data = unpack_response(client.request(pack_request("bls", ["generate"])))

        # 4. register_prepare protx
        register_prepare = unpack_response(client.request(pack_request("protx", ["register_prepare",
                                                                            collateral["hash"],
                                                                            collateral["txout"],
                                                                            "{}:19999".format(data.externalip),
                                                                            owner_address,
                                                                            bls_data["public"],
                                                                            voting_address,
                                                                            0,
                                                                            payout_address,
                                                                            fee_address])))

        signmessage = register_prepare["signMessage"]
        tx = register_prepare["tx"]

        # 5. sign tx
        signature = unpack_response(client.request(pack_request("signmessage", [collateral["address"], signmessage])))

        # 6. register_submit protx
        register_submit = unpack_response(client.request(pack_request("protx", ["register_submit", tx, signature])))

        # 7. save masternode data
        masternode_data = {
            "collateral": collateral,
            "owner_address": owner_address,
            "voting_address": voting_address,
            "payout_address": payout_address,
            "bls_data": bls_data,
            "register_prepare": register_prepare,
            "register_submit": register_submit
        }

        with open(os.path.expanduser("./masternode.json"), "w") as f:
            f.write(json.dumps(masternode_data, indent=4))

        # it is essential to wait for the confirmation of the protx
        # -> in this automated process, it can occur if not done like this that the protx is not boardcasted
        while unpack_response(client.request(pack_request("gettransaction", [register_submit])))["confirmations"] < 1:
            time.sleep(2)

        # 8. save masternode data to dash.conf
        target = os.path.expanduser("~/.dashcore/dash.conf")
        templater.core(target, target, {
            "masternodeblsprivkey": f"masternodeblsprivkey={masternode_data['bls_data']['secret']}"})

        # 9. start masternode
        client.request(pack_request("stop"))

        while True:
            try:
                command("dashd")
            except AssertionError:
                time.sleep(2)
                continue
            break

    pprint(masternode_data)

def sentinel() -> None:

