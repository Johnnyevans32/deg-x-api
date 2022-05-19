from typing import Any


from pydantic import EmailStr

from apps.featureconfig.services.featureconfig_service import FeatureConfigService
from apps.notification.slack.services.slack_service import SlackService
from apps.user.interfaces.user_interface import (
    User,
    UserLoginInput,
    UserResetPasswordInput,
)
from apps.user.interfaces.user_token_interface import UserRefreshToken
from apps.wallet.services.wallet_service import WalletService
from core.db import client, db
from core.depends import PyObjectId
from core.utils.helper_service import HelperService
from core.utils.model_utility_service import ModelUtilityService
from bson import ObjectId


class UserService:
    walletService = WalletService()
    slackService = SlackService()
    featureConfigService = FeatureConfigService()

    def create_user(self, user: User) -> User:
        session = client.start_session()
        session.start_transaction()
        try:
            self.check_if_username_exist_and_fail(user.username)
            dict_user = user.dict(by_alias=True)
            user_obj = ModelUtilityService.model_create(User, dict_user, session)
            self.walletService.create_wallet(user_obj, session)
            session.commit_transaction()
            return user_obj
        except Exception as e:
            session.abort_transaction()
            raise e
        finally:
            session.end_session()

    def login_user(self, login_user_input: UserLoginInput) -> User:
        user_obj = self.get_user_by_email(login_user_input.email)

        if not HelperService.verify_password(
            user_obj.password, login_user_input.password
        ):
            raise Exception("wrong credentials")
        if user_obj.isVerified is False:
            raise Exception("user not verified")
        return user_obj

    def get_user_by_id(self, _id: PyObjectId) -> User:
        db_resp = db.user.find_one({"_id": ObjectId(_id), "isDeleted": False})
        if db_resp is None:
            raise ValueError("user not found")
        return User(**db_resp)

    def get_user_by_email(self, email: EmailStr = None) -> User:
        db_resp = db.user.find_one({"email": email, "isDeleted": False})
        if db_resp is None:
            raise ValueError("user not found")
        return User(**db_resp)

    def get_user_by_username(self, username: str) -> User:
        db_resp = db.user.find_one({"username": username, "isDeleted": False})
        if db_resp is None:
            raise ValueError("user not found")
        return User(**db_resp)

    def check_if_username_exist_and_fail(self, username: str = None) -> Any:
        db_resp = db.user.find_one({"username": username, "isDeleted": False})
        if db_resp is None:
            return True
        raise ValueError("username already exist")

    def update_user(
        self, email: EmailStr, password_reset_dto: UserResetPasswordInput
    ) -> None:
        user = self.get_user_by_email(email)

        new_password = HelperService.hash_password(password_reset_dto.password)

        query = {"_id": user.id, "isDeleted": False}
        record_to_update = {"password": new_password}

        ModelUtilityService.model_update(User, query, record_to_update)

    def verify_email(self, email: EmailStr) -> None:
        user = self.get_user_by_email(email)

        if not user.isVerified:
            query = {"email": email, "isDeleted": False}
            record_to_update = {"isVerified": True}

            ModelUtilityService.model_update(User, query, record_to_update)

    def hard_del_user(self, email: EmailStr) -> None:
        ModelUtilityService.model_hard_delete(User, {"email": email})

    def create_user_refresh_token(self, user: User, refresh_token: str):
        ModelUtilityService.model_find_one_and_update(
            UserRefreshToken,
            {"user": user.id, "isDeleted": False},
            {"isDeleted": True},
        )

        ModelUtilityService.model_create(
            UserRefreshToken,
            {"user": user.id, "refreshToken": refresh_token},
        )

    def get_user_refresh_token(self, refresh_token: str):
        user_refresh_token = ModelUtilityService.find_one(
            UserRefreshToken, {"refreshToken": refresh_token, "isDeleted": False}
        )

        if user_refresh_token is None:
            raise Exception("invalid refresh token")

        return user_refresh_token
