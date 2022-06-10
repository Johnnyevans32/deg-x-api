import binascii
import hashlib
import json
import os
import random
import string
import time
from functools import lru_cache, partial, wraps
from pathlib import Path
from typing import Any, Type, TypeVar

import frozendict
from itsdangerous import URLSafeTimedSerializer
from pydantic import EmailStr
from requests import request
from solcx import compile_standard, install_solc

from core.config import SECRET_KEY, settings


def timed_cache(timeout: int, maxsize: int = 128, typed: bool = False):
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize, typed=typed)(func)
        func.delta = timeout * 10 ** 9
        func.expiration = time.monotonic_ns() + func.delta

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            args = tuple(
                [frozendict(arg) if isinstance(arg, dict) else arg for arg in args]
            )
            kwargs = {
                k: frozendict(v) if isinstance(v, dict) else v
                for k, v in kwargs.items()
            }
            if time.monotonic_ns() >= func.expiration:
                func.cache_clear()
                func.expiration = time.monotonic_ns() + func.delta
            return func(*args, **kwargs)

        wrapped_func.cache_info = func.cache_info
        wrapped_func.cache_clear = func.cache_clear
        return wrapped_func

    return wrapper_cache


def timer_func(func):
    # This function shows the execution time of
    # the function object passed
    def wrap_func(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        print(f"Function {func.__name__!r} executed in {(t2-t1):.4f}s")
        return result

    return wrap_func


class Utils:
    T = TypeVar("T")

    @staticmethod
    def generate_random(
        length: int = 12, chars=string.ascii_letters + string.digits
    ) -> str:
        return "".join(random.choice(chars) for _ in range(length))

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storing."""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
        pwdhash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode("ascii")

    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify a stored password against one provided by user"""
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwd_hash = hashlib.pbkdf2_hmac(
            "sha512", provided_password.encode("utf-8"), salt.encode("ascii"), 100000
        )
        pwd_hash = binascii.hexlify(pwd_hash).decode("ascii")
        return pwd_hash == stored_password

    @staticmethod
    def generate_confirmation_token(email: EmailStr = None) -> str | bytes:
        if email is None:
            raise Exception("email for token generation cant be null")
        serializer = URLSafeTimedSerializer(SECRET_KEY)
        return serializer.dumps(email, salt=settings.SECURITY_PASSWORD_SALT)

    @staticmethod
    def confirm_token(
        token: str, expiration=settings.SERIALIZER_TOKEN_EXPIRATION_IN_SEC
    ):
        serializer = URLSafeTimedSerializer(SECRET_KEY)
        email = serializer.loads(
            token, salt=settings.SECURITY_PASSWORD_SALT, max_age=expiration
        )
        return email

    @lru_cache
    @staticmethod
    def get_compiled_sol(contract_file_name: str, version: str):

        with open(Path(f"./solidity/{contract_file_name}.sol"), "r") as file:
            contract_file = file.read()

        install_solc(version)

        # Solidity source code
        compiled_sol = compile_standard(
            {
                "language": "Solidity",
                "sources": {f"{contract_file_name}.sol": {"content": contract_file}},
                "settings": {
                    "outputSelection": {
                        "*": {
                            "*": [
                                "abi",
                            ]
                        }
                    }
                },
            },
            solc_version=version,
        )

        abi = compiled_sol["contracts"][f"{contract_file_name}.sol"][
            f"{contract_file_name}"
        ]["abi"]

        return abi

    @staticmethod
    def get_abi_network_explorer(contract_address: str):
        try:
            response = request(
                "GET",
                "https://api.etherscan.io/api?module=contract&action=getabi&address="
                + contract_address,
            )
            response_json = response.json()
            abi_json = json.loads(response_json["result"])

            return abi_json
        except Exception as e:
            print(e)

    @staticmethod
    def parse_obj(generic_class: Type[T], obj: Any):
        return list(
            map(
                partial(Utils.to_class_object, generic_class),
                obj,
            )
        )

    @staticmethod
    def to_class_object(
        genericClass: Type[T],
        _dict: dict,
    ) -> T:
        return genericClass(**_dict)  # type: ignore [call-arg]
