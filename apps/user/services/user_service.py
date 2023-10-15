from typing import Any

from fastapi import BackgroundTasks
from pydantic import EmailStr

from apps.featureconfig.services.featureconfig_service import FeatureConfigService
from apps.notification.slack.services.slack_service import SlackService
from apps.user.interfaces.user_interface import (
    User,
    UserLoginInput,
    UserResetPasswordInput,
    UserUpdateDTO,
)
from apps.user.interfaces.user_token_interface import UserRefreshToken
from apps.wallet.services.wallet_service import WalletService
from apps.wallet.interfaces.wallet_interface import Wallet
from core.db import client
from core.depends.get_object_id import PyObjectId
from core.utils.aes import EncryptedDTO
from core.utils.model_utility_service import ModelUtilityService, UpdateAction
from core.utils.utils_service import NotFoundInRecordException, Utils


class UserService:
    walletService = WalletService()
    slackService = SlackService()
    featureConfigService = FeatureConfigService()
    backgroundTasks = BackgroundTasks()

    async def create_user(self, user: User) -> tuple[User, Wallet, EncryptedDTO]:
        session = client.start_session()
        session.start_transaction()
        try:
            assert user.username, "username can not be null"
            await self.check_if_username_exist_and_fail(user.username)
            dict_user = user.dict(by_alias=True, exclude_none=True)
            user_obj = await ModelUtilityService.model_create(User, dict_user, session)
            wallet, encrypted_seed = await self.walletService.create_wallet(
                user_obj, session
            )
            session.commit_transaction()
            return user_obj, wallet, encrypted_seed
        except Exception as e:
            session.abort_transaction()
            raise e
        finally:
            session.end_session()

    async def login_user(self, login_user_input: UserLoginInput) -> User:
        user_obj = await self.get_user_by_query(
            {"email": login_user_input.email, "isDeleted": False}
        )

        assert user_obj.password, "invalid credentails"
        if not Utils.verify_password(user_obj.password, login_user_input.password):
            raise Exception("wrong credentials")
        if not user_obj.isVerified:
            raise Exception("user not verified")
        return user_obj

    async def get_user_by_query(self, query: dict[str, Any]) -> User:
        user = await ModelUtilityService.find_one(User, query)
        if not user:
            raise NotFoundInRecordException(message="user not found")
        return user

    async def check_if_username_exist_and_fail(
        self, username: str, return_status: bool = False
    ) -> None | bool:
        user = await ModelUtilityService.find_one(
            User, {"username": username, "isDeleted": False}
        )

        if return_status:
            return user is None

        if user:
            raise ValueError("username already exist")

        return None

    async def update_user_password(
        self, email: EmailStr, password_reset_dto: UserResetPasswordInput
    ) -> None:
        user = await self.get_user_by_query({"email": email, "isDeleted": False})

        new_password = Utils.hash_password(password_reset_dto.password)

        query = {"_id": user.id, "isDeleted": False}
        record_to_update = {"password": new_password}

        await ModelUtilityService.model_update(User, query, record_to_update)

    async def verify_email(self, email: EmailStr) -> None:
        user = await self.get_user_by_query({"email": email, "isDeleted": False})

        if not user.isVerified:
            query = {"email": email, "isDeleted": False}
            record_to_update = {"isVerified": True}

            await ModelUtilityService.model_update(User, query, record_to_update)

    async def hard_del_user(self, email: EmailStr) -> None:
        await ModelUtilityService.model_hard_delete(User, {"email": email})

    async def create_user_refresh_token(self, user: User, refresh_token: str) -> None:
        assert user.id, "user id not found"

        await ModelUtilityService.model_create(
            UserRefreshToken,
            UserRefreshToken(user=user.id, refreshToken=refresh_token).dict(
                by_alias=True, exclude_none=True
            ),
        )
        await ModelUtilityService.model_find_one_and_update(
            UserRefreshToken,
            {"user": user.id, "isDeleted": False},
            {"isDeleted": True},
        )

    async def get_user_refresh_token(self, refresh_token: str) -> UserRefreshToken:
        user_refresh_token = await ModelUtilityService.find_one(
            UserRefreshToken, {"refreshToken": refresh_token, "isDeleted": False}
        )

        if not user_refresh_token:
            raise Exception("refresh token not found")

        return user_refresh_token

    async def get_user_socket_ids(self, user_id: PyObjectId) -> list[str]:
        user = await self.get_user_by_query({"_id": user_id, "isDeleted": False})
        socketIds = user.socketIds
        return socketIds or []

    async def update_user_socket_id(
        self, user_id: PyObjectId, socket_id: str, socket_status: str
    ) -> User:
        updateAction = {"connect": UpdateAction.PUSH, "disconnect": UpdateAction.PULL}
        user = await ModelUtilityService.model_find_one_and_update(
            User,
            {"_id": user_id, "isDeleted": False},
            {"socketIds": socket_id},
            updateAction=updateAction[socket_status],
        )
        assert user, "user not found"

        return user

    async def update_user_details(self, user: User, payload: UserUpdateDTO) -> None:

        query = {"_id": user.id, "isDeleted": False}
        record_to_update = payload.dict(by_alias=True, exclude_none=True)

        await ModelUtilityService.model_update(User, query, record_to_update)
