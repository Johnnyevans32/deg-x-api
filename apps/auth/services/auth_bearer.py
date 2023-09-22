from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


from apps.auth.services.jwt_service import JWTService
from apps.user.services.user_service import UserService
from apps.user.interfaces.user_interface import User
from core.utils.custom_exceptions import UnicornException
from core.utils.response_service import ResponseService


jwtService = JWTService()
responseService = ResponseService()
userService = UserService()


async def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer(auto_error=True))]
) -> User:
    try:
        user_decoded_jwt = jwtService.decode_jwt(creds.credentials, "ACCESS_TOKEN")
        if not user_decoded_jwt:
            raise UnicornException(
                status_code=403, message="Invalid token or expired token."
            )
        current_user = await userService.get_user_by_query(
            {"_id": user_decoded_jwt.user, "isDeleted": False}
        )

        return current_user
    except Exception:
        raise UnicornException(
            status_code=401, message=responseService.status_code_message[401]
        )


CurrentUser = Annotated[User, Depends(get_current_user)]
