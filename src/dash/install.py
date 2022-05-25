import subprocess
import requests
import tarfile
import sys


def sys_command(command: str) -> str:
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    out, err = process.communicate()
    code = process.returncode

    if code == 0:
        return out.decode("utf-8").strip()

    raise Exception("Error: {}".format(err.decode("utf-8").strip()))


def download(url: str, file_name: str) -> None:
    with open(file_name, "wb") as file:
        response = requests.get(f"{url}/{file_name}", stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:  # no content length header
            file.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                file.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                sys.stdout.flush()
            sys.stdout.write("\n")


def extract(file_name: str) -> None:
    tar = tarfile.open(file_name)
    tar.extractall()
    tar.close()


def layer_one() -> None:
    """
    Downloads and installs layer 1 on localhost
    """

    url = "https://github.com/dashpay/dash/releases/download/v18.0.0-rc4"
    file_name = "dashcore-18.0.0-rc4-{}-linux-gnu.tar.gz".format(sys_command("uname -m"))

    download(url, file_name)
    extract(file_name)
    sys_command("sudo install -t /usr/local/bin dashcore-*/bin/*")



