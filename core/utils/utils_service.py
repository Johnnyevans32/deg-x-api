import asyncio
import base64
import binascii
import hashlib
import json
import os
import random
import string
import time
import uuid
from functools import lru_cache, wraps
from io import BytesIO
from pathlib import Path
from typing import Any, Awaitable, Callable, List, Type, TypeVar

from PIL import Image
import requests
import qrcode
from async_lru import alru_cache
from boto3 import client
from frozendict.core import frozendict
from itsdangerous import URLSafeTimedSerializer
from pydantic import EmailStr
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from requests import request
from solcx import compile_standard, install_solc
from web3 import Web3

from core.config import settings
from core.utils.loggly import logger


class NotFoundInRecordException(Exception):
    def __init__(
        self, model: str | None = None, message: str = "payload not found"
    ) -> None:
        self.model = model
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.model} -> {self.message}"


def timed_cache(  # type: ignore
    timeout: int, maxsize: int = 128, typed: bool = False, asyncFunction: bool = False
):
    """
    timed_cache: give lru cache time expiration ability

    Args:
        timeout (int): duration of cache power in minutes
        maxsize (int, optional): _description_. Defaults to 128.
        typed (bool, optional): _description_. Defaults to False.
    """

    def wrapper_cache(func):  # type: ignore
        func = (
            alru_cache(maxsize=maxsize, typed=typed)(func)
            if asyncFunction
            else lru_cache(maxsize=maxsize, typed=typed)(func)
        )
        func.delta = (timeout * 10**9) * 60
        func.expiration = time.monotonic_ns() + func.delta

        @wraps(func)
        def wrapped_func(*args, **kwargs):  # type: ignore

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

        wrapped_func.cache_info = func.cache_info  # type: ignore
        wrapped_func.cache_clear = func.cache_clear  # type: ignore
        return wrapped_func

    return wrapper_cache


def timer_func(func: Callable[[Any, Any], Any]) -> Any:
    """
    timer_func This function shows the execution time of the function object passed

    Args:
        func (Callable): the function in question
    """

    def wrap_func(*args: Any, **kwargs: Any) -> Any:
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
        length: int = 12, chars: str = string.ascii_letters + string.digits
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
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        return serializer.dumps(email, salt=settings.SECURITY_PASSWORD_SALT)

    @staticmethod
    def confirm_token(
        token: str, expiration: int = settings.SERIALIZER_TOKEN_EXPIRATION_IN_SEC
    ) -> Any:
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        email = serializer.loads(
            token, salt=settings.SECURITY_PASSWORD_SALT, max_age=expiration
        )
        return email

    @staticmethod
    @timed_cache(10000000, asyncFunction=True)
    async def get_compiled_sol(contract_file_name: str, version: str) -> Any:
        with open(Path(f"./solidity/{contract_file_name}.sol"), "r") as file:
            contract_file = file.read()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, install_solc, version, True)

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
    def get_evm_reverted_reason(err: Any) -> str:
        if type(err) == str:
            return err
        code = str(err["data"]).replace("Reverted ", "")
        if code == "Reverted":
            return err

        reason = Web3.to_text(text="0x" + code)
        return reason

    @staticmethod
    def get_abi_network_explorer(contract_address: str) -> Any:
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
        _dict: dict[str, Any],
    ) -> T:
        """
        to_class_object: convert to dict to class object

        Args:
            genericClass (Type[T]): class object to convert to
            _dict (dict): dict to convert from

        Returns:
            T: converted object result
        """
        return genericClass(**_dict)

    @staticmethod
    def create_qr_image(data_to_encode: Any = "Deg X") -> str:
        # Creating an instance of QRCode class
        qr = qrcode.QRCode(version=2, error_correction=qrcode.ERROR_CORRECT_Q)

        # Adding data to the instance 'qr'
        qr.add_data(data_to_encode)

        qr.make(fit=True)
        response = requests.get(
            "https://res.cloudinary.com/dfbjysygb/image/upload/"
            "v1668763106/rsz_1degx-pre_o8m3tt.png",
            stream=True,
        )
        logo = Image.open(response.raw)
        logo = logo.resize((50, 50))
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=RadialGradiantColorMask(edge_color=(218, 112, 214)),
            embeded_image=logo,
            eye_drawer=RoundedModuleDrawer(),
        )

        buffer = BytesIO()
        img.save(buffer)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        image_url = Utils.upload_file(data_to_encode, img_base64)
        return image_url

    @staticmethod
    def upload_file(file_name: str, base64_data: str) -> str:
        if not settings.IS_DEV:
            return (
                "https://s3-us-west-2.amazonaws.com/verifi-app-bucket/"
                + "1bad0760-22c5-4ac6-bcac-c963193e393063080868bcec8b55dc441a19"
            )
        else:
            s3_client = client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )

        file_name = Utils.generate_unique_file_name(file_name)
        s3_client.put_object(
            Body=base64.b64decode(base64_data),
            Bucket=settings.S3_BUCKET_NAME,
            Key=file_name,
        )
        # get object url
        object_url = Utils.get_file_url_location(s3_client, file_name)
        return object_url

    @staticmethod
    def generate_unique_file_name(file_name: str) -> str:
        return "{}{}".format(uuid.uuid4(), file_name)

    @staticmethod
    def get_file_url_location(s3_client: Any, file_name: str) -> str:
        location = s3_client.get_bucket_location(Bucket=settings.S3_BUCKET_NAME)[
            "LocationConstraint"
        ]
        return "https://s3-{}.amazonaws.com/{}/{}".format(
            location, settings.S3_BUCKET_NAME, file_name
        )

    @staticmethod
    async def promise_all(
        promises: List[Awaitable[T]], return_exceptions: bool = True
    ) -> List[T]:
        async def await_and_return(awaitable: Awaitable[Any]) -> Any:
            return await awaitable

        tasks = [asyncio.create_task(await_and_return(promise)) for promise in promises]
        return [await task for task in tasks]

    @staticmethod
    def sendMessageToBros(
        message: str = "THIS IS AN AUTOMATED MESSAGE FOR BIRTHDAY "
        "SHOUTOUTS \n GROUP ID: 2347089954501-1602500956@g.us \n created by demigod💀",
        mentions: str = "",
    ) -> None:
        url = "https://api.ultramsg.com/instance65730/messages/chat"

        payload = json.dumps(
            {
                "token": "sq0xt4ynr6ehlqcb",
                "to": "2347089954501-1602500956@g.us",
                "body": message,
                "priority": 10,
                "referenceId": "",
                "msgId": "",
                "mentions": mentions,
            }
        )
        headers = {"Content-Type": "application/json"}
        response = requests.request(
            "POST",
            url,
            data=payload,
            headers=headers,
        )
        print(response.text)
        print(response)
