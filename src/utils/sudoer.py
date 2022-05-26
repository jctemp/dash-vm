from src.utils.command import command
import os

def prompt_sudo():
    ret = 0
    if os.geteuid() != 0:
        msg = "[sudo] password for %u:"

        try:
            command("sudo -v -p '%s'" % msg)
        except AssertionError as e:
            ret = 1
    return ret

