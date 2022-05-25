import tarfile


def extract(filename: str) -> None:
    tar = tarfile.open(filename)
    tar.extractall()
    tar.close()
