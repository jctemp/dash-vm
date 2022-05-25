import requests

from exception import RpcException

def unpack_response(response: any, throw_exception: bool = True) -> any:
    if response.status_code == 200:
        return response.json()["result"]
    elif throw_exception:
        raise RpcException(response, response.status_code, response.json()["error"]["message"])
    else:
        return response.json()["error"]
