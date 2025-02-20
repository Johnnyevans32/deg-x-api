from pymongo.errors import DuplicateKeyError

from apps.auth.interfaces.auth_interface import AuthResponse
from apps.auth.services.jwt_service import JWTService
from apps.user.interfaces.user_interface import (
    User,
    UserLoginInput,
    UserResetPasswordInput,
)
from apps.user.services.user_service import UserService
from core.utils.custom_exceptions import UnicornException
from core.utils.utils_service import Utils
from apps.wallet.services.wallet_service import WalletService


class AuthService:
    userService = UserService()
    jwtService = JWTService()
    walletService = WalletService()

    async def create_account(self, user: User) -> AuthResponse:
        try:
            assert user.password, "password is required"
            user.password = Utils.hash_password(user.password)
            user_reg_res = await self.userService.create_user(user)
            user_created, wallet, seed = user_reg_res
            return AuthResponse(user=user_created, wallet=wallet, seed=seed)

        except DuplicateKeyError:
            raise Exception('"User with {user.email} already exist"')

    async def login_user(self, user: UserLoginInput) -> AuthResponse:
        user_logged_in = await self.userService.login_user(user)
        assert user_logged_in.id, "id is null"
        access_token = self.jwtService.sign_jwt(user_logged_in.id, "ACCESS_TOKEN")
        refresh_token = self.jwtService.sign_jwt(user_logged_in.id, "REFRESH_TOKEN")
        await self.userService.create_user_refresh_token(user_logged_in, refresh_token)
        return AuthResponse(
            accessToken=access_token,
            refreshToken=refresh_token,
        )

    async def me(self, user: User) -> AuthResponse:
        wallet = await self.walletService.get_user_default_wallet_without_error(user)
        return AuthResponse(user=user, wallet=wallet)

    async def update_user_password(
        self, token: str, password_reset_dto: UserResetPasswordInput
    ) -> str:
        email = Utils.confirm_token(token)
        if not email:
            raise UnicornException("Email invalid or expired")
        await self.userService.update_user_password(email, password_reset_dto)

        return "success"

    async def verify_email(self, token: str) -> None:
        email = Utils.confirm_token(token)
        if not email:
            raise UnicornException("Email invalid or expired")
        await self.userService.verify_email(email)

    async def authenticate_refresh_token(self, refresh_token: str) -> AuthResponse:
        refresh_token_obj = await self.userService.get_user_refresh_token(refresh_token)
        self.jwtService.decode_jwt(refresh_token_obj.refreshToken, "REFRESH_TOKEN")
        token = self.jwtService.sign_jwt(refresh_token_obj.user, "ACCESS_TOKEN")
        return AuthResponse(accessToken=token, refreshToken=refresh_token)
