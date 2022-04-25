import time

import jwt

from core.config import settings


class JWTService:
    @staticmethod
    def sign_jwt(user_id: str) -> str:
        payload = {
            "user_id": user_id,
            "expires": time.time() + settings.TOKEN_EXPIRATION_IN_SEC,
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

        return token

    @staticmethod
    def decode_jwt(token: str) -> dict:
        decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        if decoded_token["expires"] < time.time():
            raise Exception("Token has expired")
        return decoded_token
