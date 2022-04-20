import dashup.helper.utils as utils
import os

def purge():
    dashcore = os.path.expanduser("~/.dashcore")
    dash_path = os.path.expanduser("/usr/local/bin")
    dash_bin = ["dashd", "dash-cli", "dash-tx",
                "dash-qt", "docker-compose", "test-dash"]

    utils.execute_process("pkill dashd")
    utils.remove(dashcore)
    for bin in dash_bin:
        utils.remove(f"{dash_path}/{bin}")

    utils.execute_process("crontab -r > /dev/null")
