import requests
import json


class rpcClientException(Exception):

    def __init__(self, response: any, status_code: int, error_message: str):
        self.response = response
        self.status_code = status_code
        self.error_message = error_message

    def __str__(self):
        return f"{self.status_code}: {self.error_message}"


class rpcClient:

    def __init__(self, host: str, port: int, username: str, password: str, timeout: int = 10):
        self.username = username
        self.password = password
        self.url = f"http://{host}:{port}"

        self.headers = {'content-type': 'application/json'}
        self.headers['Authorization'] = f"Basic {self.username}:{self.password}"

        self.timeout = timeout

    def sendRequest(self, method: str, params: list = [], wallet_name: str = None) -> dict:
        '''
        Send request to RPC server
        @param method: method to call
        @param params: parameters to pass to method
        @param wallet_name: which wallet to work with
        '''

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
            response = requests.post(url, data=json.dumps(payload), headers=self.headers,
                                     auth=(self.username, self.password), timeout=self.timeout)
        except:
            raise rpcClientException(None, -1, "Could not post request")

        if response.status_code != 200:
            raise rpcClientException(
                response, response.status_code, f'Request failed.\nCheck the url "{url}" and credentials "{self.username}:{self.password}"')

        res = response.json()

        if "result" not in res:
            raise rpcClientException(response, -1, "Response is not valid")

        return res["result"]

    def printException(self, exception: rpcClientException, traceback: bool = False):
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
            print(traceback.format_exc())

    def setUrl(self, host: str, port: int):
        self.url = f"http://{host}:{port}"

    def __str__(self):
        return "rpcClient\n" + \
            f"    username: {self.username}\n" + \
            f"    password: {self.password}\n" + \
            f"    url: {self.url}"


# listwallets
# loadwallet
# createwallet
# getwalletinfo
# unloadwallet
# dumpwallet
# upgradetohd
# dumpprivkey
# getaddressinfo

# getmininginfo
# generate => change to generateToAddress

# mnsync
# stop

# bls
# spork
# protx
# quorum
# masternode
# signmessage

# getblockchaininfo
# getbestchainlock

# sendtoaddress
# gettransaction
# gettxout



# test = rpcClient("localhost", 19998, "dashrpc", "password")

# try:
#     print(test.sendRequest("getmininginfo", []))
# except rpcClientException as e:
#     test.printException(e)
