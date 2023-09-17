from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import DecodeError

from apps.auth.services.jwt_service import JWTService
from apps.user.services.user_service import UserService
from core.utils.custom_exceptions import UnicornException
from core.utils.response_service import ResponseService


class JWTBearer(HTTPBearer):
    jwtService = JWTService()
    responseService = ResponseService()
    userService = UserService()

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        try:
            credentials = await super(JWTBearer, self).__call__(request)
            if not credentials:
                raise UnicornException(
                    status_code=403, message="Invalid authorization code."
                )
            if not credentials.scheme == "Bearer":
                raise UnicornException(
                    status_code=403, message="Invalid authentication scheme."
                )

            user_decoded_jwt = self.jwtService.decode_jwt(
                credentials.credentials, "ACCESS_TOKEN"
            )
            if not user_decoded_jwt:
                raise UnicornException(
                    status_code=403, message="Invalid token or expired token."
                )

            request.state.user = await self.userService.get_user_by_query(
                {"_id": user_decoded_jwt.user, "isDeleted": False}
            )

            return credentials
        except DecodeError:
            raise UnicornException(
                status_code=403, message="Invalid authorization code."
            )

        except Exception:
            raise UnicornException(
                status_code=401, message=self.responseService.status_code_message[401]
            )
