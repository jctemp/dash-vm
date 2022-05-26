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

    def request(self, payload: dict, wallet_name: str = None) -> Response:
        """
        Send request to RPC server
        @param payload: data which is sent to dashd
        @param wallet_name: which wallet to work with
        """

        url = self.url
        if wallet_name:
            url = f"{self.url}/{wallet_name}"

        try:
            return requests.post(url, data=json.dumps(payload), headers=self.headers,
                                 auth=(self.username, self.password))
        except RpcException:
            raise RpcException(None, -1, "Could not post request")

    def __str__(self):
        return "rpcClient\n" + \
               f"    username: {self.username}\n" + \
               f"    password: {self.password}\n" + \
               f"    url: {self.url}"
