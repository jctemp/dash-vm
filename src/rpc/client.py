import requests
import json

from src.rpc.exception import RpcException


class Client:

    def __init__(self, host: str = "localhost", port: int = 19998, username: str = "dashrpc",
                 password: str = "password"):
        self.username = username
        self.password = password
        self.url = f"http://{host}:{port}"  # change to https if you use rpc over internet
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    def request(self, payload: dict, wallet_name: str = None) -> requests.Response:
        """
        Send request to RPC server
        @param payload: data which is sent to dashd
        @param wallet_name: which wallet to work with
        """

        url = self.url
        if wallet_name:
            url = f"{self.url}/wallet/{wallet_name}"

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
