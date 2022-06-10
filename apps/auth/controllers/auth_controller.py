from fastapi import APIRouter, Response
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError
from starlette import status

from apps.auth.interfaces.auth_interface import AuthResponse
from apps.auth.services.auth_service import AuthService
from apps.auth.services.google_service import GoogleService
from apps.notification.email.services.email_service import EmailService
from apps.user.interfaces.user_interface import (
    User,
    UserLoginInput,
    UserResetPasswordInput,
)
from apps.user.services.user_service import UserService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.utils_service import Utils
from core.utils.response_service import ResponseService, get_response_model

router = APIRouter(prefix="/api/v1/account", tags=["Auth 🔐"])


emailService = EmailService()
userService = UserService()
authService = AuthService()
responseService = ResponseService()
googleService = GoogleService()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=get_response_model(AuthResponse, "RegisterResponse"),
)
async def register_user(user: User, request: UnicornRequest, res: Response):
    try:
        request.app.logger.info(f"creating user with email - {user.email}")
        resp = authService.create_account(user)
        request.app.logger.info(f"sending verification email to - {user.email}")
        emailService.send_verification(user)
        request.app.logger.info(f"done sending verification email to - {user.email}")
        request.app.logger.info(f"created user with email - {user.email} successfully")
        return responseService.send_response(
            res,
            status.HTTP_201_CREATED,
            "User Registration Successful, check your email to"
            " complete verification process",
            resp,
        )
    except DuplicateKeyError:
        request.app.logger.error(
            f"Error registering user because " f"- User with {user.email} already exist"
        )
        return responseService.send_response(
            res,
            status.HTTP_409_CONFLICT,
            f"User with {user.email} already exist",
            use_class_message=False,
        )
    except Exception as e:
        # raise e
        request.app.logger.error(f"Error registering user {user.email}, {str(e)}")
        return responseService.send_response(
            res, status.HTTP_400_BAD_REQUEST, f"User Registration Failed: {str(e)}"
        )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=get_response_model(AuthResponse, "LoginResponse"),
)
async def login_user(
    login_input: UserLoginInput, request: UnicornRequest, res: Response
):
    try:
        request.app.logger.info(f"logging in user with email - {login_input.email}")
        resp = authService.login_user(login_input)
        request.app.logger.info(f"logging user with email - {login_input.email}")
        return responseService.send_response(
            res, status.HTTP_200_OK, "User Log in Successful", resp
        )
    except Exception as e:
        # raise e
        request.app.logger.error(f"Error logging user {login_input.email}, {str(e)}")
        return responseService.send_response(
            res, status.HTTP_400_BAD_REQUEST, f"User Login Failed: {str(e)}"
        )


@router.get("/confirm/{token}")
async def confirm_email(request: UnicornRequest, res: Response, token):
    try:
        email = Utils.confirm_token(token)
        if not email:
            request.app.logger.error("Email invalid or expired")
            return responseService.send_response(
                res, status.HTTP_400_BAD_REQUEST, "Email invalid or expired"
            )
        request.app.logger.info(f"verifying user with email - {email}")
        userService.verify_email(email)

        request.app.logger.info(f"verified user with email - {email}")
        return responseService.send_response(
            res, status.HTTP_200_OK, "email verified successfully"
        )
    except Exception as e:
        request.app.logger.error(f"Error verifying user email {str(e)}")
        return responseService.send_response(
            res, status.HTTP_400_BAD_REQUEST, f"Error verifying user email {str(e)}"
        )


@router.get("/forgotten_password_link/{user_email}")
async def send_forgotten_password_link(
    request: UnicornRequest, res: Response, user_email: EmailStr
):
    try:
        user = userService.get_user_by_email(user_email)
        request.app.logger.info(
            f"sending forgotten password link to user with email - {user.email}"
        )
        emailService.send_forgotten_password_link(user)
        request.app.logger.info(
            f"done sending forgotten password link email to user with email - {user.email}"
        )
        return responseService.send_response(
            res, status.HTTP_200_OK, "forgotten password link has been sent."
        )
    except Exception as e:
        request.app.logger.error(
            f"Error sending user forgotten password link - {str(e)}"
        )
        return responseService.send_response(
            res,
            status.HTTP_400_BAD_REQUEST,
            f"Error sending user forgotten password link - {str(e)}",
        )


@router.put("/update-password/{token}")
async def update_password(
    request: UnicornRequest,
    res: Response,
    token,
    password_reset_dto: UserResetPasswordInput,
):
    try:
        email = Utils.confirm_token(token)
        if not email:
            request.app.logger.error("Email invalid or expired")
            return responseService.send_response(
                res, status.HTTP_400_BAD_REQUEST, "Email invalid or expired"
            )
        request.app.logger.info(f"resetting password for user with email - {email}")
        userService.update_user(email, password_reset_dto)

        request.app.logger.info(
            f"done resetting password for user with email - {email}"
        )
        return responseService.send_response(
            res, status.HTTP_200_OK, "user password updated successfully"
        )
    except Exception as e:
        request.app.logger.error(f"Error  resetting password for user {str(e)}")
        return responseService.send_response(
            res,
            status.HTTP_400_BAD_REQUEST,
            f"Error resetting password for user {str(e)}",
        )


@router.get("/resend-verification/{user_email}")
async def resend_confirmation(
    request: UnicornRequest, res: Response, user_email: EmailStr
):
    try:
        user = userService.get_user_by_email(user_email)
        request.app.logger.info(
            f"resending verification email to user with email - {user.email}"
        )
        emailService.send_verification(user)
        request.app.logger.info(
            f"done resending verification email to user with email - {user.email}"
        )
        return responseService.send_response(
            res, status.HTTP_200_OK, "new confirmation email has been sent."
        )
    except Exception as e:
        request.app.logger.error(f"Error resending user confirmation email - {str(e)}")
        return responseService.send_response(
            res,
            status.HTTP_400_BAD_REQUEST,
            f"Error resending user confirmation email - {str(e)}",
        )


@router.post(
    "/oauth",
    status_code=status.HTTP_201_CREATED,
    response_model=get_response_model(AuthResponse, "OAuthRegisterResponse"),
)
async def oauth_sign_in(user_id: str, request: UnicornRequest, res: Response):
    try:
        request.app.logger.info(f"authenticating user with oauth id - {user_id}")
        user_resp = await googleService.verify_oauth_sign_in(user_id)
        request.app.logger.info(f"done authenticating user with oauth id - {user_id}")
        return responseService.send_response(
            res,
            status.HTTP_201_CREATED,
            "user successfully authenticated",
            user_resp,
        )
    except Exception as e:
        request.app.logger.error(f"Error authenticating user {str(e)}")
        return responseService.send_response(
            res,
            status.HTTP_400_BAD_REQUEST,
            f"user authentication failed: {str(e)}",
        )


@router.post(
    "/refresh-access-token",
    status_code=status.HTTP_201_CREATED,
)
async def get_access_token(refresh_token: str, request: UnicornRequest, res: Response):
    try:
        request.app.logger.info("authenticating refresh token for user")
        user_resp = authService.authenticate_refresh_token(refresh_token)
        request.app.logger.info("done authenticating refresh token for user ")
        return responseService.send_response(
            res,
            status.HTTP_201_CREATED,
            "access token retrieved",
            user_resp,
        )
    except Exception as e:
        request.app.logger.error(
            f"Error authenticating refresh token for user {str(e)}"
        )
        return responseService.send_response(
            res,
            status.HTTP_400_BAD_REQUEST,
            f"refresh token authentication failed: {str(e)}",
        )
