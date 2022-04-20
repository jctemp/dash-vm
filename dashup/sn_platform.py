import dashup.helper.rpc as rpc
import dashup.helper.utils as utils
import time


def setup() -> None:
    rpcsettings = {"wallet": "", "address": "localhost",
                   "port": 19998, "username": "dashrpc", "password": "password"}

    try:
        rpc.stop(rpcsettings)
        time.sleep(2)
        rpc.start()
        rpc.sync(rpcsettings)
        rpc.test(rpcsettings)

        activate_sporks(rpcsettings)
        wait_for_quorum(rpcsettings)
        wait_for_chainlock(rpcsettings)
    except Exception as e:
        utils.error("Failed to activate sporks")
        utils.error(e)
        exit(1)

    utils.success("Network ready to setup masternodes")


def activate_sporks(rpcsettings: dict = None) -> dict:
    '''
    Activate sporks
    '''
    utils.info("Activating sporks")
    settings = rpc.check_rpcsettings(rpcsettings)

    result = rpc.sporks(rpcsettings)

    for key in result:
        rpc.rpc(settings["url"], "spork", [key, 0],
                settings["username"], settings["password"])

    result = rpc.sporks(rpcsettings)
    return result


def wait_for_quorum(rpcsettings: dict = None) -> dict:
    '''
    Wait for quorum
    '''
    utils.info("Waiting for quorum")
    found = False
    qorum = ""
    while not found:
        rpc.generate_blocks(1, rpcsettings)
        result = rpc.quorum(rpcsettings)
        for key in result:
            if len(result[key]) > 0:
                found = True
                qorum = key
        time.sleep(1)

    result = rpc.quorum(rpcsettings)
    return {qorum: result[qorum]}


def wait_for_chainlock(rpcsettings: dict = None) -> None:
    '''
    Wait for chainlock
    '''
    utils.info("Waiting for chainlock")
    while not rpc.chainlock(rpcsettings):
        rpc.generate_blocks(1, rpcsettings)
        time.sleep(1)