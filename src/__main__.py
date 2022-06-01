from rich import traceback
from rich.console import Console
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table

import src
from src.utils.addresses import addresses

from src.nodes.core import core
from src.nodes.core import CoreData

from src.utils.command import command
from src.rpc.client import Client
from src.rpc.packing import pack_request, unpack_response
from src.rpc.commands import generate_collateral, generate_platform_keys, generate_spork

traceback.install()


def menu(options: dict) -> None:
    """
    there are three options for the options' parameter:
    - seednode: initial node to set up a devnet
    - masternode: create a masternode for a devnet
    - fullnode: vanilla dash fullnode
    @param options: key option name and value is the description
    @return:
    """
    console = Console(color_system="auto")
    console.print(Text("Choose an option:", style="bold blue"))

    choices = []
    for key, value in options.items():
        console.print(f"[green]{key}:[/] [i dim]{value}[/]")
        choices.append(key)

    node_type = Prompt.ask("Node type", default=choices[0], choices=choices)

    table = Table()
    table.add_column("Name")
    table.add_column("Address")
    for name, address in addresses():
        table.add_row(name, address)

    console.print(table)

    data: CoreData = CoreData()

    externalip = Prompt.ask("externalip")
    data.externalip = externalip if externalip else None

    if node_type == "masternode":
        sporkaddr = Prompt.ask("sporkaddr")
        data.sporkaddr = sporkaddr if sporkaddr else None

        sporkkey = Prompt.ask("sporkkey")
        data.sporkkey = sporkkey if sporkkey else None

        masternodeblsprivkey = Prompt.ask("masternodeblsprivkey")
        data.masternodeblsprivkey = masternodeblsprivkey if masternodeblsprivkey else None

        addnode = Prompt.ask("addnode")
        data.addnode = addnode if addnode else None

    elif node_type == "fullnode":

        sporkaddr = Prompt.ask("sporkaddr")
        data.sporkaddr = sporkaddr if sporkaddr else None

        sporkkey = Prompt.ask("sporkkey")
        data.sporkkey = sporkkey if sporkkey else None

        addnode = Prompt.ask("addnode")
        data.addnode = addnode if addnode else None

    core(data)

    # seed()


# menu({
#     "seednode": "inital node to setup a devnet",
#     "masternode": "create a masternode for a devnet",
#     "fullnode": "vanilla dash fullnode"
# })

c = Client()
# print(generate_collateral(c))
print(generate_platform_keys(c))
print(generate_spork(c))