from typing import Union

from apps.auth.services.jwt_service import JWTService
from apps.user.interfaces.user_interface import User, UserLoginInput
from apps.user.services.user_service import UserService
from core.utils.helper_service import HelperService


class AuthService:
    userService = UserService()
    jwtService = JWTService()

    def create_account(self, user: User) -> dict[str, User]:
        user.password = HelperService.hash_password(user.password)
        user_created = self.userService.create_user(user)
        return {"user": user_created}

    def login_user(self, user: UserLoginInput) -> dict[str, Union[User, str]]:
        user_logged_in = self.userService.login_user(user)
        token = self.jwtService.sign_jwt(str(user_logged_in.id))
        return {"user": user_logged_in, "token": token}
