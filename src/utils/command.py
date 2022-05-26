import subprocess


def command(cmd: str) -> str:
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    out, err = process.communicate()
    code = process.returncode

    if code == 0:
        return out.decode("utf-8").strip()

    raise AssertionError("Error: {}".format(err.decode("utf-8").strip()))
