import os
import sys
import shutil
from dataclasses import dataclass

from src.templates.dashconf import config as dash_conf
from src.utils.command import command
from src.utils.download import download
from src.utils.extract import extract
from src.utils.templater import core as core_template
from src.utils.sudoer import prompt_sudo

from rich.progress import Console
from rich.traceback import install as install_traceback

install_traceback()


@dataclass
class CoreData:
    externalip: str = None
    sporkaddr: str = None
    sporkkey: str = None
    masternodeblsprivkey: str = None
    addnode: list = None


def core(data: CoreData) -> None:
    """
    Downloads and installs layer 1 on localhost
    """

    already_installed = True

    try:
        command("which dashd")
    except AssertionError:
        already_installed = False

    if already_installed:
        print("Dash Core is already installed")
        return

    if prompt_sudo() != 0:
        print("You must run this as root")
        sys.exit(1)

    with Console().status("Installing Layer 1", spinner="arc") as console:

        # currently hardcoded but should be dynamic in the future
        url = "https://github.com/dashpay/dash/releases/download/v18.0.0-rc4"
        filename = "dashcore-18.0.0-rc4-{}-linux-gnu.tar.gz".format(command("uname -m"))

        working = os.path.expanduser("./tmp")

        if os.path.exists(working):
            try:
                shutil.rmtree(working)
            except OSError:
                pass

        os.mkdir(working)
        os.chdir(working)

        download(url, filename)
        extract(filename)
        command("sudo install -t /usr/local/bin dashcore-*/bin/*")

        os.chdir("..")
        try:
            shutil.rmtree(working)
        except OSError:
            pass

        target = os.path.expanduser("~/.dashcore")

        if os.path.exists(target):
            try:
                shutil.rmtree(target)
            except OSError:
                pass

        os.mkdir(target)
        os.chdir(target)

        values = {}
        for key, value in data.__dict__.items():
            if value is not None:
                # join values with \n if they are lists
                if isinstance(value, list):
                    value = "\n".join("{}={}:19999".format(key, item) for item in value)
                    values[key] = value
                else:
                    values[key] = "{}={}".format(key, value)

        core_template(dash_conf, "./dash.conf", values)
