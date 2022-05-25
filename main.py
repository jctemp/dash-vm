from rich import traceback
traceback.install()

import sys
import os

# create a command line interface application
from rich.console import Console
from rich.text import Text
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.style import Style


# there are three options for the options parameter:
# - seednode: inital node to setup a devnet
# - masternode: create a masternode for a devnet
# - fullnode: vanilla dash fullnode

# display menu with options
def display_menu(options: dict) -> None:
    console = Console(color_system="auto")
    # "[bold red]Dashup - Simple Devnet Setup"

    # create a window


    console.print(Text("Choose an option:", style="bold blue"))
    for key, value in options.items():
        console.print(f"[green]{key}:[/] [i dim]{value}[/]")



# display_menu({
#     "seednode": "inital node to setup a devnet",
#     "masternode": "create a masternode for a devnet", 
#     "fullnode": "vanilla dash fullnode"
# })

from rich import print
from rich.columns import Columns

if len(sys.argv) < 2:
    print("Usage: python columns.py DIRECTORY")
else:
    directory = os.listdir(sys.argv[1])
    columns = Columns(directory, equal=True, expand=True)
    print(columns)