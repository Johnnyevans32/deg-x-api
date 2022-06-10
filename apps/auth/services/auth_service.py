from apps.auth.services.jwt_service import JWTService
from apps.user.interfaces.user_interface import User, UserLoginInput
from apps.user.services.user_service import UserService
from core.utils.utils_service import Utils


class AuthService:
    userService = UserService()
    jwtService = JWTService()

    def create_account(self, user: User) -> dict[str, User]:
        user.password = Utils.hash_password(user.password)
        user_created = self.userService.create_user(user)
        return {"user": user_created}

    def login_user(self, user: UserLoginInput) -> dict[str, User | str]:
        user_logged_in = self.userService.login_user(user)
        access_token = self.jwtService.sign_jwt(str(user_logged_in.id), "ACCESS_TOKEN")
        refresh_token = self.jwtService.sign_jwt(
            str(user_logged_in.id), "REFRESH_TOKEN"
        )
        self.userService.create_user_refresh_token(user_logged_in, refresh_token)
        return {
            "user": user_logged_in,
            "accessToken": access_token,
            "refreshToken": refresh_token,
        }

    def authenticate_refresh_token(self, refresh_token: str):
        refresh_token_obj = self.userService.get_user_refresh_token(refresh_token)
        self.jwtService.decode_jwt(refresh_token_obj.refreshToken, "REFRESH_TOKEN")
        token = self.jwtService.sign_jwt(str(refresh_token_obj.user), "ACCESS_TOKEN")
        return {"accessToken": token, "refreshToken": refresh_token}
