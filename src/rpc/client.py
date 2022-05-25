import requests
import json

from requests import Response

from exception import RpcException


class Client:

    def __init__(self, host: str = "localhost", port: int = 19998, username: str = "dashrpc",
                 password: str = "password"):
        self.username = username
        self.password = password
        self.url = f"https://{host}:{port}"
        self.headers = {'content-type': 'application/json', 'Authorization': f"Basic {self.username}:{self.password}"}

    def request(self, method: str, params=None, wallet_name: str = None) -> Response:
        """
        Send request to RPC server
        @param method: method to call
        @param params: parameters to pass to method
        @param wallet_name: which wallet to work with
        """

        if params is None:
            params = []
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0
        }

        url = self.url
        if wallet_name:
            url = f"{self.url}/{wallet_name}"

        try:
            return requests.post(url, data=json.dumps(payload), headers=self.headers,
                                 auth=(self.username, self.password))
        except RpcException:
            raise RpcException(None, -1, "Could not post request")

    @staticmethod
    def print_exception(exception: RpcException, traceback: bool = False):
        '''
        print rpcClientException to stdout
        @param exception: rpcClientException to print
        @param traceback: print traceback
        '''

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

    def set_url(self, host: str, port: int):
        self.url = f"https://{host}:{port}"

    def __str__(self):
        return "rpcClient\n" + \
               f"    username: {self.username}\n" + \
               f"    password: {self.password}\n" + \
               f"    url: {self.url}"
