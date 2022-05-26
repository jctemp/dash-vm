import tarfile


def extract(filename: str) -> None:

    with tarfile.open(filename, "r:gz") as tar:
        tar.extractall()
