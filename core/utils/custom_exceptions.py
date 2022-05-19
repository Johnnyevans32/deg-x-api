from typing import Any


class UnicornException(Exception):
    def __init__(self, message: str, status_code: int, data: Any = None):
        self.message = message
        self.status_code = status_code
        self.data = data
