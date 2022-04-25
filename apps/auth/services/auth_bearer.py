from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from jwt import DecodeError

from apps.auth.services.jwt_service import JWTService
from apps.user.services.user_service import UserService
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
                    raise HTTPException(
                        status_code=403, detail="Invalid authentication scheme."
                    )
                else:
                    payload = self.verify_jwt(credentials.credentials)
                    if not payload:
                        raise HTTPException(
                            status_code=403, detail="Invalid token or expired token."
                        )
                    request.state.user = self.userService.get_user_by_id(
                        payload["user_id"]
                    )
                    return credentials.credentials
            else:
                raise HTTPException(
                    status_code=403, detail="Invalid authorization code."
                )
        except DecodeError:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

        except Exception:
            raise HTTPException(
                status_code=401, detail=self.responseService.status_code_message[401]
            )

    def verify_jwt(self, jwt_token: str) -> dict:
        payload = self.jwtService.decode_jwt(jwt_token)

        return payload
