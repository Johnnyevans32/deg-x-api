from fastapi import BackgroundTasks, Response, status, APIRouter
from fastapi_restful.cbv import cbv
from pydantic import EmailStr

from apps.auth.services.auth_bearer import CurrentUser
from apps.auth.interfaces.auth_interface import AuthResponse
from apps.auth.services.auth_service import AuthService
from apps.cloudplatform.interfaces.cloud_interface import CloudProvider, IDType
from apps.cloudplatform.services.cloud_service import CloudService
from apps.notification.email.services.email_service import EmailService
from apps.user.interfaces.user_interface import (
    User,
    UserLoginInput,
    UserResetPasswordInput,
)
from apps.user.services.user_service import UserService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseModel, ResponseService

router = APIRouter(prefix="/account", tags=["Auth 🔐"])


@cbv(router)
class AuthController:
    emailService = EmailService()
    userService = UserService()
    authService = AuthService()
    responseService = ResponseService()
    cloudService = CloudService()

    @router.post(
        "/register",
        status_code=status.HTTP_201_CREATED,
        response_model_by_alias=False,
    )
    async def register_user(
        self,
        user: User,
        request: UnicornRequest,
        res: Response,
        background_tasks: BackgroundTasks,
    ) -> ResponseModel[AuthResponse]:
        try:
            request.app.logger.info(f"creating user with email - {user.email}")
            resp = await self.authService.create_account(user)
            background_tasks.add_task(self.emailService.send_verification, user)
            request.app.logger.info(
                f"created user with email - {user.email} successfully"
            )
            return self.responseService.send_response(
                res,
                status.HTTP_201_CREATED,
                "User Registration Successful, check your email to"
                " complete verification process",
                resp,
            )
        except Exception as e:
            # raise e
            request.app.logger.error(f"Error registering user {user.email}, {str(e)}")
            return self.responseService.send_response(
                res, status.HTTP_400_BAD_REQUEST, f"User Registration Failed: {str(e)}"
            )

    @router.post(
        "/login",
        status_code=status.HTTP_200_OK,
        response_model_by_alias=False,
    )
    async def login_user(
        self, login_input: UserLoginInput, request: UnicornRequest, res: Response
    ) -> ResponseModel[AuthResponse]:
        try:
            request.app.logger.info(f"logging in user with email - {login_input.email}")
            resp = await self.authService.login_user(login_input)
            request.app.logger.info(f"logging user with email - {login_input.email}")
            return self.responseService.send_response(
                res, status.HTTP_200_OK, "User Log in Successful", resp
            )
        except Exception as e:
            # raise e
            request.app.logger.error(
                f"Error logging user {login_input.email}, {str(e)}"
            )
            return self.responseService.send_response(
                res, status.HTTP_400_BAD_REQUEST, f"User Login Failed: {str(e)}"
            )

    @router.get(
        "/me",
        status_code=status.HTTP_200_OK,
        response_model_by_alias=False,
    )
    async def me(
        self,
        request: UnicornRequest,
        res: Response,
        current_user: CurrentUser,
    ) -> ResponseModel[AuthResponse]:
        try:
            resp = await self.authService.me(current_user)
            return self.responseService.send_response(
                res, status.HTTP_200_OK, "success", resp
            )
        except Exception as e:
            return self.responseService.send_response(
                res, status.HTTP_400_BAD_REQUEST, f"{str(e)}"
            )

    @router.get("/verify/{token}")
    async def verify_email(
        self, request: UnicornRequest, res: Response, token: str
    ) -> ResponseModel[None]:
        try:
            request.app.logger.info(f"verifying user with token - {token}")
            await self.authService.verify_email(token)
            request.app.logger.info(f"verified user with token - {token}")
            return self.responseService.send_response(
                res, status.HTTP_200_OK, "email verified successfully"
            )
        except Exception as e:
            request.app.logger.error(f"Error verifying user email {str(e)}")
            return self.responseService.send_response(
                res, status.HTTP_400_BAD_REQUEST, f"Error verifying user email {str(e)}"
            )

    @router.get("/forgotten_password_link/{user_email}")
    async def send_forgotten_password_link(
        self,
        request: UnicornRequest,
        res: Response,
        user_email: EmailStr,
        background_tasks: BackgroundTasks,
    ) -> ResponseModel[None]:
        try:
            user = await self.userService.get_user_by_query(
                {"email": user_email, "isDeleted": False}
            )
            request.app.logger.info(
                f"sending forgotten password link to user with email - {user.email}"
            )
            background_tasks.add_task(
                self.emailService.send_forgotten_password_link, user
            )
            request.app.logger.info(
                f"done sending forgotten password link email to user with email - {user.email}"
            )
            return self.responseService.send_response(
                res, status.HTTP_200_OK, "forgotten password link has been sent."
            )
        except Exception as e:
            request.app.logger.error(
                f"Error sending user forgotten password link - {str(e)}"
            )
            return self.responseService.send_response(
                res,
                status.HTTP_400_BAD_REQUEST,
                f"Error sending user forgotten password link - {str(e)}",
            )

    @router.put("/password/{token}")
    async def update_user_password(
        self,
        request: UnicornRequest,
        res: Response,
        token: str,
        password_reset_dto: UserResetPasswordInput,
    ) -> ResponseModel[None]:
        try:
            request.app.logger.info(f"resetting password for user with token - {token}")
            await self.authService.update_user_password(token, password_reset_dto)
            request.app.logger.info(
                f"done resetting password for user with token - {token}"
            )
            return self.responseService.send_response(
                res, status.HTTP_200_OK, "user password updated successfully"
            )
        except Exception as e:
            request.app.logger.error(f"Error  resetting password for user {str(e)}")
            return self.responseService.send_response(
                res,
                status.HTTP_400_BAD_REQUEST,
                f"Error resetting password for user {str(e)}",
            )

    @router.get("/resend-verification/{user_email}")
    async def resend_confirmation(
        self,
        request: UnicornRequest,
        res: Response,
        user_email: EmailStr,
        background_tasks: BackgroundTasks,
    ) -> ResponseModel[None]:
        try:
            user = await self.userService.get_user_by_query(
                {"email": user_email, "isDeleted": False}
            )
            request.app.logger.info(
                f"resending verification email to user with email - {user.email}"
            )

            background_tasks.add_task(self.emailService.send_verification, user)
            request.app.logger.info(
                f"done resending verification email to user with email - {user.email}"
            )
            return self.responseService.send_response(
                res, status.HTTP_200_OK, "new confirmation email has been sent."
            )
        except Exception as e:
            request.app.logger.error(
                f"Error resending user confirmation email - {str(e)}"
            )
            return self.responseService.send_response(
                res,
                status.HTTP_400_BAD_REQUEST,
                f"Error resending user confirmation email - {str(e)}",
            )

    @router.post(
        "/oauth-signin",
        status_code=status.HTTP_201_CREATED,
        response_model_by_alias=False,
    )
    async def oauth_signin(
        self,
        request: UnicornRequest,
        res: Response,
        cloud_provider: CloudProvider,
        auth_token: str,
        token_type: IDType = IDType.AccessToken,
    ) -> ResponseModel[AuthResponse]:
        try:
            request.app.logger.info("authenticating user with oauth")
            user_resp = await self.cloudService.oauth_signin(
                cloud_provider, auth_token, token_type
            )
            request.app.logger.info("done authenticating user with oauth")
            return self.responseService.send_response(
                res,
                status.HTTP_201_CREATED,
                "user successfully authenticated",
                user_resp,
            )
        except Exception as e:
            request.app.logger.error(f"Error authenticating user {str(e)}")
            return self.responseService.send_response(
                res,
                status.HTTP_400_BAD_REQUEST,
                f"user authentication failed: {str(e)}",
            )

    @router.post(
        "/refresh-access-token",
        status_code=status.HTTP_201_CREATED,
    )
    async def get_access_token(
        self, request: UnicornRequest, res: Response, refresh_token: str
    ) -> ResponseModel[AuthResponse]:
        try:
            request.app.logger.info("authenticating refresh token for user")
            user_resp = await self.authService.authenticate_refresh_token(refresh_token)
            request.app.logger.info("done authenticating refresh token for user ")
            return self.responseService.send_response(
                res,
                status.HTTP_201_CREATED,
                "access token retrieved",
                user_resp,
            )
        except Exception as e:
            request.app.logger.error(
                f"Error authenticating refresh token for user {str(e)}"
            )
            return self.responseService.send_response(
                res,
                status.HTTP_400_BAD_REQUEST,
                f"refresh token authentication failed: {str(e)}",
            )
