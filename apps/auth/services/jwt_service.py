import jwt
import pendulum
from pydantic import BaseModel

from core.config import settings
from core.depends.get_object_id import PyObjectId


class UserJWTPayload(BaseModel):
    user: PyObjectId
    expiresAt: float


class JWTService:
    TOKEN_TYPE: dict[str, dict[str, str | int]] = {
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
    def sign_jwt(user_id: PyObjectId, token_type: str) -> str:
        expiration_time = int(JWTService.TOKEN_TYPE[token_type]["expiresIn"])
        encode_key = str(JWTService.TOKEN_TYPE[token_type]["key"])
        payload = {
            "user": str(user_id),
            "expiresAt": pendulum.now().add(minutes=expiration_time).float_timestamp,
        }

        token = jwt.encode(payload, encode_key, algorithm="HS256")

        return token

    @staticmethod
    def decode_jwt(token: str, token_type: str) -> UserJWTPayload:
        encode_key = str(JWTService.TOKEN_TYPE[token_type]["key"])

        decoded_token = UserJWTPayload(
            **jwt.decode(token, encode_key, algorithms=["HS256"])
        )

        if decoded_token.expiresAt < pendulum.now().float_timestamp:
            raise Exception("Token has expired")

        return decoded_token
