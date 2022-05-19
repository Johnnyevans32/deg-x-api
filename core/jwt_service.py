from typing import Union
import jwt
import pendulum

from core.config import settings


class JWTService:
    TOKEN_TYPE: dict[str, dict[str, Union[str, int]]] = {
        "ACCESS_TOKEN": {
            "key": settings.ACCESS_TOKEN_JWT_SECRET,
            "expiresIn": settings.ACCESS_TOKEN_EXPIRATION,
        },
        "REFRESH_TOKEN": {
            "key": settings.REFRESH_TOKEN_JWT_SECRET,
            "expiresIn": settings.REFRESH_TOKEN_EXPIRATION,
        },
    }

    @staticmethod
    def sign_jwt(user_id: str, token_type: str) -> str:
        expiration_time = int(JWTService.TOKEN_TYPE[token_type]["expiresIn"])
        encode_key = str(JWTService.TOKEN_TYPE[token_type]["key"])
        payload = {
            "user_id": user_id,
            "expires": pendulum.now().add(minutes=expiration_time).float_timestamp,
        }

        token = jwt.encode(payload, encode_key, algorithm="HS256")

        return str(token, "utf-8")

    @staticmethod
    def decode_jwt(token: str, token_type: str) -> dict:
        encode_key = str(JWTService.TOKEN_TYPE[token_type]["key"])
        decoded_token = jwt.decode(token, encode_key, algorithms=["HS256"])
        if decoded_token["expires"] < pendulum.now().float_timestamp:
            raise Exception("Token has expired")
        return decoded_token
