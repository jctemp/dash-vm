import os.path
import json
from pathlib import Path

from rich.prompt import IntPrompt
from rich.pretty import pprint

from src.rpc.client import Client
from src.rpc.commands import generate_spork, generate_platform_keys, generate_collateral, sync
from src.utils import templater

from rich.progress import Console
from rich.traceback import install as install_traceback

install_traceback()


def seed() -> None:

    mn_count = IntPrompt.ask("Masternode count: ", default=3)

    with Console().status("Generating Devnet Data", spinner="arc") as console:
        client = Client()

        sync(client)

        spork_address, spork_key = generate_spork(client)
        platform_keys, key_names = generate_platform_keys(client)

        target = os.path.expanduser("~/.dashcore/dash.conf")
        templater.core(target, target,{
            "sporkaddr": f"sporkaddr={spork_address}",
            "sporkkey": f"sporkkey={spork_key}"})

        spork = {"address": spork_address, "key": spork_key}
        platform = {key_names[0]: platform_keys[key_names[0]],
                    key_names[1]: platform_keys[key_names[1]],
                    key_names[2]: platform_keys[key_names[2]],
                    key_names[3]: platform_keys[key_names[3]]}

        collaterals = {}
        for i in range(mn_count):
            collateral_address, collateral_hash, collateral_key = generate_collateral(client)
            collaterals[i] = {"address": collateral_address, "hash": collateral_hash, "key": collateral_key}

        # write to file
        with open(os.path.expanduser("./spork.json"), "w") as f:
            f.write(json.dumps(spork, indent=4))

        with open(os.path.expanduser("./platform.json"), "w") as f:
            f.write(json.dumps(platform, indent=4))

        with open(os.path.expanduser("./collaterals.json"), "w") as f:
            f.write(json.dumps(collaterals, indent=4))

    pprint(spork, expand_all=True)
    pprint(platform, expand_all=True)
    pprint(collaterals, expand_all=True)
