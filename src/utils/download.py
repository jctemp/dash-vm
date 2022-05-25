import requests


def download(url: str, filename: str) -> None:
    """
    Downloads filename from url
    """

    with open(filename, "wb") as file:
        response = requests.get(f"{url}/{filename}", stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:  # no content length header
            file.write(response.content)
        else:
            for data in response.iter_content(chunk_size=4096):
                file.write(data)
