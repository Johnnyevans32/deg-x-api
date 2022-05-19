from fastapi import Request
from fastapi.security import HTTPBearer
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

    async def __call__(self, request: Request):
        try:
            credentials = await super(JWTBearer, self).__call__(request)
            if credentials:
                if not credentials.scheme == "Bearer":
                    raise UnicornException(
                        status_code=403, message="Invalid authentication scheme."
                    )
                else:
                    payload = self.verify_jwt(credentials.credentials)
                    if not payload:
                        raise UnicornException(
                            status_code=403, message="Invalid token or expired token."
                        )
                    request.state.user = self.userService.get_user_by_id(
                        payload["user_id"]
                    )
                    return credentials.credentials
            else:
                raise UnicornException(
                    status_code=403, message="Invalid authorization code."
                )
        except DecodeError:
            raise UnicornException(
                status_code=403, message="Invalid authorization code."
            )

        except Exception:
            raise UnicornException(
                status_code=401, message=self.responseService.status_code_message[401]
            )

    def verify_jwt(self, jwt_token: str) -> dict:
        print(jwt_token)
        payload = self.jwtService.decode_jwt(jwt_token, "ACCESS_TOKEN")

        return payload
