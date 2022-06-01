import os.path
from dataclasses import dataclass
import json

from rich.prompt import IntPrompt

from src.rpc.client import Client
from src.rpc.commands import generate_spork, generate_platform_keys
from src.utils import templater

from rich.progress import Console
from rich.traceback import install as install_traceback

install_traceback()


@dataclass
class SeedData:
    pass


def seed(data: SeedData) -> None:

    mn_count = IntPrompt.ask("Masternode count: ", default=3)

    with Console().status("Preparing Devnet", spinner="arc") as console:
        client = Client()

        Console().print("Generating spork address and key")
        spork_address, spork_key = generate_spork(client)

        Console().print("Generating platform keys")
        platform_keys, key_names = generate_platform_keys(client)

        Console().print("Saving data")
        with open("spork", "w") as f:
            f.write(json.dumps({spork_address: spork_key}, indent=4))

        with open("platform_keys", "w") as f:
            f.write(json.dumps({key_names[0]: platform_keys[key_names[0]],
                                key_names[1]: platform_keys[key_names[1]],
                                key_names[2]: platform_keys[key_names[2]],
                                key_names[3]: platform_keys[key_names[3]]}, indent=4))

        target = os.path.expanduser("~/.dashcore/dash.conf")

        # TODO: set spork key and address
        templater.core(target, target, {})

        for i in range(mn_count):



            # 1. generate blocks to get funds until there is 1000 Dash per masternode
            # 2. create an address
            # 3. send money to the address
            # 4. save address with transaction hash
            pass

    pass

