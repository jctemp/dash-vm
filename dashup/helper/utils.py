import shutil
import netifaces
import subprocess
import requests
import tarfile
import re
import os

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def error(message: str):
    '''
    Print error message
    @param message: message to print
    '''
    print(f"{bcolors.FAIL}[ERROR]{bcolors.ENDC} {message}")


def warning(message: str):
    '''
    Print warning message
    @param message: message to print
    '''
    print(f"{bcolors.WARNING}[WARNING]{bcolors.ENDC} {message}")


def success(message: str):
    '''
    Print info message
    @param message: message to print
    '''
    print(f"{bcolors.OKGREEN}[OK]{bcolors.ENDC} {message}")


def info(message: str):
    '''
    Print info message
    @param message: message to print
    '''
    print(f"{bcolors.OKCYAN}[INFO]{bcolors.ENDC} {message}")


def title(message: str):
    '''
    Print title
    @param message: message to print
    '''
    print(f"{bcolors.BOLD}{message}{bcolors.ENDC}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class re_template:
    NUMBERS = r'[0-9]+'
    WORDS = r'[a-zA-Z]+'
    HEX = r'[0-9a-fA-F]+'


def hline():
    '''
    Print horizontal line
    '''
    print("━" * os.get_terminal_size().columns)


def get_input(message: str, regex: str) -> any:
    '''
    Get input from user
    @param message: message to print
    @param regex: regex to validate input
    '''
    warning(r"USER INPUT REQUIRED")

    input_value = input(message)
    while not re.match(regex, input_value):
        error(r"INVALID INPUT")
        input_value = input(message)

    return input_value


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def execute_process(command: str) -> dict:
    '''
    Execute process
    @param command: command to execute
    @param shell: execute command in shell
    '''
    child = subprocess.Popen(command, shell=True, executable="/bin/bash")
    child.wait()
    out, err = child.communicate()
    code = child.returncode

    if code == 0:
        return {'status': True, 'out': out}
    return {'status': False, 'err': err}


def clone_repository(repo_url: str, destination: str, branch: str = "master") -> dict:
    '''
    Clone repository from github
    @param repo_url: url of repository to clone
    @param destination: destination to clone repository to
    @param branch: branch to clone
    '''
    if os.path.exists(f"{destination}/{branch}"):
        return {"status": False, "message": "Destination already exists"}

    return execute_process(f"git clone -q -b {branch} {repo_url} {destination}")


def download_file(url: str, file_name: str = None) -> bool:
    '''
    Download file from url
    @param url: url to download file from
    @param file_name: name of file to download
    '''
    if os.path.exists(file_name):
        return False
    try:
        with open(file_name, 'wb') as f:
            response = requests.get(url)
            f.write(response.content)
    except:
        return False

    return True


def extract_tar(file_name: str, destination=".") -> str:
    '''
    Extract tar file
    @param file_name: name of tar file to extract
    @param destination: destination to extract file to
    '''
    if not os.path.exists(file_name):
        return ""

    destination = os.path.abspath(destination)
    with tarfile.open(file_name, 'r') as tar:
        tar.extractall(destination)
        tar_info = tar.getmembers()

    directories = [file.name for file in tar_info if file.isdir()]
    files = [file.name for file in tar_info if not file.isdir()]

    top_dir = [d for d in directories if "/" not in d]
    top_file = [f for f in files if "/" not in f]

    return os.path.join(destination, top_dir[0] if len(top_dir) == 1 else top_file[0])


def remove(file_name: str) -> bool:
    '''
    Remove file, directory or symbolic link from file system if it exists
    @param file_name: file to remove
    '''
    # check if file exists
    if not os.path.exists(file_name):
        return False

    if os.path.isdir(file_name):
        response = execute_process(f"sudo rm -r {file_name}")
    else:
        response = execute_process(f"sudo rm {file_name}")

    return response['status']


def get_ip_address() -> list:
    '''
    Get ip address of interface
    @param interface: interface to get ip address from
    '''

    # get ip address of available ipv4 interfaces
    addresses = []
    for iface in netifaces.interfaces():
        if iface == "lo":
            continue
        if netifaces.AF_INET in netifaces.ifaddresses(iface):
            addresses.append(netifaces.ifaddresses(iface)[
                             netifaces.AF_INET][0]['addr'])

    return addresses


def install_from_directory(src: str, dst: str) -> bool:
    '''
    Install application from directory
    @param src: source directory
    @param dst: destination directory
    '''
    if not os.path.exists(dst):
        return False

    if not os.path.exists(src):
        return False

    result = execute_process(f'sudo install -t {dst} {src}/*')
    return result[r"status"]


def replace_in_file(file_name: str, search_string: str, replace_string: str) -> bool:
    '''
    Replace string in file
    @param file_name: file to replace string in
    @param search_string: string to search for
    @param replace_string: string to replace with
    '''
    if not os.path.exists(file_name) or not os.path.isfile(file_name):
        return False

    with open(file_name, 'r') as f:
        content = f.read()

    content = re.sub(search_string, replace_string, content, 0, re.MULTILINE)
    # content = content.replace(search_string, replace_string)

    with open(file_name, 'w') as f:
        f.write(content)

    return True


def append_to_crontab(job: str) -> bool:
    '''
    Append command to crontab
    @param command: command to append to crontab
    '''
    pipe = subprocess.Popen('crontab -l', shell=True,
                            executable="/bin/bash", stdout=subprocess.PIPE)

    pipe.wait()
    pipe.returncode

    content = ""
    if pipe.returncode == 0:
        content = pipe.communicate()[0].decode('utf-8')

    if job in content:
        return True

    content += f'{job}\n'

    with open('/tmp/crontab', 'w') as f:
        f.write(content)

    execute_process('crontab /tmp/crontab')

    return True


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# test = execute_process("ls -l")
# print(test)
# # test = clone_repository("https://github.com/dashpay/dash.git", "test_dir")
# # print(test)
# test = download_file(
#     "https://github.com/dashpay/dash/releases/download/v0.17.0.3/dashcore-0.17.0.3-x86_64-linux-gnu.tar.gz", "test.tar.gz")
# print(test)
# test = extract_tar("test.tar.gz", "test_dir_2")
# print(test)
# test = remove("test.tar.gz")
# print(test)
# test = remove_directory("test_dir_2")
# print(test)
# test = get_ip_address()
# print(test)
# test = is_installed("git")
# print(test)
# test = install_from_directory("test_dir", "/home/jctemp/test_dir")
# print(test)
# test = replace_in_file("test.txt", "test", "test_2")
# print(test)
