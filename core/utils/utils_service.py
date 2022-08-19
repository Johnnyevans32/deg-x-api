import binascii
import hashlib
import json
import os
import random
import string
import time
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Callable, Type, TypeVar

import eth_utils
import frozendict
from async_lru import alru_cache
from itsdangerous import URLSafeTimedSerializer
from pydantic import EmailStr
from requests import request
from solcx import compile_standard, install_solc

from core.config import SECRET_KEY, settings
from core.utils.loggly import logger


def timed_cache(
    timeout: int, maxsize: int = 128, typed: bool = False, asyncFunction=False
):
    """
    timed_cache: give lru cache time expiration ability

    Args:
        timeout (int): duration of cache power in minutes
        maxsize (int, optional): _description_. Defaults to 128.
        typed (bool, optional): _description_. Defaults to False.
    """

    def wrapper_cache(func):
        func = (
            alru_cache(maxsize=maxsize, typed=typed)(func)
            if asyncFunction
            else lru_cache(maxsize=maxsize, typed=typed)(func)
        )
        func.delta = (timeout * 10**9) * 60
        func.expiration = time.monotonic_ns() + func.delta

        @wraps(func)
        def wrapped_func(*args, **kwargs):

            args = tuple(
                [
                    frozendict.frozendict(arg) if isinstance(arg, dict) else arg
                    for arg in args
                ]
            )
            kwargs = {
                k: frozendict.frozendict(v) if isinstance(v, dict) else v
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


def timer_func(func: Callable):
    """
    timer_func This function shows the execution time of the function object passed

    Args:
        func (Callable): the function in question
    """

    def wrap_func(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        logger.info(f"Function {func.__name__!r} executed in {(t2-t1):.4f}s")
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
    def verify_password(stored_password: str, provided_password: str) -> bool:
        """Verify a stored password against one provided by user"""
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwd_hash = hashlib.pbkdf2_hmac(
            "sha512", provided_password.encode("utf-8"), salt.encode("ascii"), 100000
        )
        decoded_pwd_hash = binascii.hexlify(pwd_hash).decode("ascii")
        return decoded_pwd_hash == stored_password

    @staticmethod
    def generate_confirmation_token(email: EmailStr) -> str | bytes:
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

    @lru_cache(10)
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
    def get_evm_reverted_reason(err: Any):
        code = str(err["data"]).replace("Reverted ", "")
        if code == "Reverted":
            return err

        reason = eth_utils.to_text("0x" + code)
        return reason

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
            logger.error(f"Error getting ABI from network provider - {str(e)}")

    @staticmethod
    def to_class_object(
        genericClass: Type[T],
        _dict: dict,
    ) -> T:
        """
        to_class_object: convert to dict to class object

        Args:
            genericClass (Type[T]): class object to convert to
            _dict (dict): dict to convert from

        Returns:
            T: converted object result
        """
        return genericClass(**_dict)  # type: ignore [call-arg]
