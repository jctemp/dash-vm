import json


class RpcException(Exception):

    def __init__(self, response: any, status_code: int, error_message: str):
        self.response = response
        self.status_code = status_code
        self.error_message = error_message

    def __str__(self):
        return f"{self.status_code}: {self.error_message}"


def print_exception(exception: RpcException, traceback: bool = False):
    """
    print rpcClientException to stdout
    @param exception: rpcClientException to print
    @param traceback: print traceback
    """
    print(f"{exception.status_code}: {exception.error_message}")
    if exception.response is not None and exception.response.text is not None and \
            exception.response.text != "":

        res = json.loads(exception.response.text)
        if "error" in res:
            print(f"    code: {res['error']['code']}")
            print(f"    message: {res['error']['message']}")
        else:
            print(f"    {res}")

    if traceback:
        print(traceback)
