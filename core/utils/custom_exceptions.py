from logging import Logger
from typing import Any

from fastapi import Request


class UnicornException(Exception):
    def __init__(self, message: str, status_code: int = 400, data: Any = None):
        self.message = message
        self.status_code = status_code
        self.data = data


class UnicornApp:
    logger: Logger


class UnicornRequest(Request):
    app: UnicornApp
