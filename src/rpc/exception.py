class RpcException(Exception):

    def __init__(self, response: any, status_code: int, error_message: str):
        self.response = response
        self.status_code = status_code
        self.error_message = error_message

    def __str__(self):
        return f"{self.status_code}: {self.error_message}"

