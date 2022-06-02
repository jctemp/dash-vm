import os.path
import json
import time

from src.rpc.client import Client
from src.rpc.commands import generate_spork, generate_platform_keys, generate_collateral, sync
from src.rpc.packing import pack_request, unpack_response

from src.utils import templater
from src.utils.command import command

from rich.prompt import IntPrompt
from rich.pretty import pprint
from rich.progress import Console
from rich.traceback import install as install_traceback


install_traceback()


def seed() -> None:

    mn_count = IntPrompt.ask("Masternode count: ", default=3)

    with Console().status("Generating Devnet Data", spinner="arc") as console:
        client = Client()

        sync(client)

        # 1. generate network data
        spork_address, spork_key = generate_spork(client)
        platform_keys, key_names = generate_platform_keys(client)

        # 2. set spork
        target = os.path.expanduser("~/.dashcore/dash.conf")
        templater.core(target, target,{
            "sporkaddr": f"sporkaddr={spork_address}",
            "sporkkey": f"sporkkey={spork_key}"})

        # 3. prepare data to write
        spork = {"address": spork_address, "key": spork_key}
        platform = {key_names[0]: platform_keys[key_names[0]],
                    key_names[1]: platform_keys[key_names[1]],
                    key_names[2]: platform_keys[key_names[2]],
                    key_names[3]: platform_keys[key_names[3]]}

        # 4. generate collaterals
        collaterals = {}
        for i in range(mn_count):
            collateral_address, collateral_hash, collateral_key = generate_collateral(client)
            collaterals[i] = {"address": collateral_address, "hash": collateral_hash, "key": collateral_key}

        # 5. write data to files
        with open(os.path.expanduser("./spork.json"), "w") as f:
            f.write(json.dumps(spork, indent=4))

        with open(os.path.expanduser("./platform.json"), "w") as f:
            f.write(json.dumps(platform, indent=4))

        with open(os.path.expanduser("./collaterals.json"), "w") as f:
            f.write(json.dumps(collaterals, indent=4))

        # 6. restart node
        client.request(pack_request("stop"))

        while True:
            try:
                command("dashd")
            except AssertionError:
                time.sleep(2)
                continue
            break

        # 7. activate spork
        spork_list = unpack_response(client.request(pack_request("spork", ["active"])))
        for key in spork_list:
            client.request(pack_request("spork", [key, 0]))

    pprint(spork, expand_all=True)
    pprint(platform, expand_all=True)
    pprint(collaterals, expand_all=True)
