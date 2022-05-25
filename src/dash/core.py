from src.utils.download import download
from src.utils.command import command
from src.utils.extract import extract

from src.utils.templater import core as core_template
from src.templates.dashconf import config as dash_conf

import os, shutil

from dataclasses import dataclass


@dataclass
class Dash:
    externalip: str = None
    sporkaddr: str = None
    sporkkey: str = None
    masternodeblsprivkey: str = None
    addnode: list[str] = None


def core(data: Dash) -> None:
    """
    Downloads and installs layer 1 on localhost
    """

    # # currently hardcoded but should be dynamic in the future
    # url = "https://github.com/dashpay/dash/releases/download/v18.0.0-rc4"
    # filename = "dashcore-18.0.0-rc4-{}-linux-gnu.tar.gz".format(command("uname -m"))

    # download(url, filename)
    # extract(filename)
    # command("sudo install -t /usr/local/bin dashcore-*/bin/*")

    # target = os.path.expanduser("~/.dashcore")

    # if os.path.exists(target):
    #     shutil.rmtree(target)

    # os.mkdir(os.path.expanduser("~/.dashcore"))
    # os.chdir(os.path.expanduser("~/.dashcore"))

    values = {
        "externalip": data.externalip,
        "sporkaddr": data.sporkaddr,
        "sporkkey": data.sporkkey,
        "masternodeblsprivkey": data.masternodeblsprivkey,
        "addnode": data.addnode
    }

    core_template(dash_conf, "dash.conf", values)


core(Dash())
