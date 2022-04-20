import dashup.helper.utils as utils
import dashup.helper.rpc as rpc
import shutil
import json
import time
import os


def setup() -> None:
    '''
    Setup dash node and configuration (fullnode)
    '''
    utils.hline()
    utils.title("Setting up dashd")
    try:
        install("/vagrant/downloads.json")
        config("/vagrant/template.dash.conf")
        utils.append_to_crontab(
            "*/5 * * * * [ -d ~/.dashcore ] && pgrep dashd || /usr/local/bin/dashd")
        rpc.start()
        time.sleep(2)
        rpc.sync()

    except Exception as e:
        utils.error("Setup failed")
        utils.hline()
        e.with_traceback()
        exit(1)
    utils.success("Setup complete")
    utils.hline()


def install(downloads: str) -> bool:
    '''
    utils.
    Install dashd
    @param downloads: json file with download information
    name "core" is used to define "url"
    '''
    utils.info("Installing dashd")

    # check if dashd is installed
    if shutil.which('dashd'):
        return True

    if not os.path.exists(downloads) or not os.path.isfile(downloads):
        utils.error('Cannot find ' + downloads)
        return False

    # load json file
    url = ""
    with open(downloads, 'r') as f:
        downloads = json.load(f)
        if 'core' not in downloads:
            utils.error("No core in downloads json file")
            return False
        url = downloads['core']

    # create temporary directory with os
    os.mkdir('./tmp')
    os.chdir('./tmp')

    # download, extract and install dashd
    file = "core.tar.gz"
    utils.download_file(url, file)
    result = utils.extract_tar(file)
    result = utils.install_from_directory(
        result + "/bin", "/usr/local/bin")

    if not result:
        utils.error("Installation failed")
        return False

    # remove downloaded files
    os.chdir("..")
    utils.remove("./tmp")
    return True


def config(config: str, override=False) -> bool:
    '''
    Set dashd configuration file
    @param config: configuration file to use
    '''
    utils.info("Setting dashd configuration file")

    target_dir = os.path.expanduser('~/.dashcore')
    if not override and os.path.exists(target_dir):
        return True

    # check if config file exists
    if not os.path.exists(config) or not os.path.isfile(config):
        utils.error("Config file does not exist")
        return False

    # select ip of machine
    addresses = utils.get_ip_address()
    address = ""
    if len(addresses) == 1:
        address = addresses[0]
    else:
        utils.info("Possible ip addresses:")
        for addr in addresses:
            print(f'   {addresses.index(addr) + 1}) {addr}')

        value = utils.get_input(
            f'Select interface to use [1-{len(addresses)}]: ', r"^[1-{}]$".format(len(addresses)))
        address = addresses[int(value) - 1]
    utils.info(f'SELECTED {address}')

    # set configuration file
    config_path = os.path.dirname(config)

    # copy template.dash.conf to dash.conf
    shutil.copyfile(config, f'{config_path}/dash.conf')
    os.chmod(f'{config_path}/dash.conf', 0o666)

    # replace ip address
    result = utils.replace_in_file(
        f'{config_path}/dash.conf', 'externalip=', f'externalip={address}')

    if not result:
        utils.error(result['message'])

    # expand ~/.dashcore to full path
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    shutil.move(f'{config_path}/dash.conf',
                f'{target_dir}/dash.conf')

    return True
