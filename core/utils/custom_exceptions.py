from logging import Logger
from typing import Any

from fastapi import Request
from starlette.datastructures import State

from apps.user.interfaces.user_interface import User


class UnicornException(Exception):
    def __init__(self, message: str, status_code: int = 400, data: Any = None):
        self.message = message
        self.status_code = status_code
        self.data = data


class UnicornState(State):
    user: User


class UnicornApp:
    logger: Logger


class UnicornRequest(Request):
    state: UnicornState
    app: UnicornApp
