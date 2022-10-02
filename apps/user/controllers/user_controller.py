# -*- coding: utf-8 -*-
from fastapi import Response, status, Depends
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter
from apps.auth.interfaces.auth_interface import AuthResponse

from apps.auth.services.auth_bearer import JWTBearer
from apps.user.interfaces.user_interface import UserUpdateDTO
from apps.user.services.user_service import UserService
from apps.wallet.services.wallet_service import WalletService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseModel, ResponseService

router = InferringRouter(prefix="/user", tags=["User 🌈"])


@cbv(router)
class UserController:
    userService = UserService()
    walletService = WalletService()
    responseService = ResponseService()

    @router.get(
        "/",
        dependencies=[Depends(JWTBearer())],
        response_model_by_alias=False,
    )
    async def get_user(
        self,
        request: UnicornRequest,
        res: Response,
    ) -> ResponseModel[AuthResponse]:
        try:
            user = request.state.user
            request.app.logger.info("getting user profile")
            wallet = await self.walletService.get_user_default_wallet(user)

            request.app.logger.info("done getting user profile")
            return self.responseService.send_response(
                res,
                status.HTTP_200_OK,
                "user details retrieved successfully",
                AuthResponse(
                    user=user,
                    wallet=wallet,
                ),
            )
        except Exception as e:
            request.app.logger.error(f"Error getting user profile- {str(e)}")
            return self.responseService.send_response(
                res,
                status.HTTP_400_BAD_REQUEST,
                f"Error getting user profile {str(e)}",
            )

    @router.put(
        "/update-profile",
        dependencies=[Depends(JWTBearer())],
        response_model_by_alias=False,
    )
    async def update_user_profile(
        self,
        request: UnicornRequest,
        res: Response,
        update_payload: UserUpdateDTO,
    ) -> ResponseModel[None]:
        try:
            user = request.state.user
            request.app.logger.info("updating user profile")
            await self.userService.update_user_details(user, update_payload)

            request.app.logger.info("done updating user profile")
            return self.responseService.send_response(
                res, status.HTTP_200_OK, "user details updated successfully"
            )
        except Exception as e:
            request.app.logger.error(f"Error updating user profile- {str(e)}")
            return self.responseService.send_response(
                res,
                status.HTTP_400_BAD_REQUEST,
                f"Error updating user profile {str(e)}",
            )

    @router.get(
        "/check-username",
        dependencies=[Depends(JWTBearer())],
        response_model_by_alias=False,
    )
    async def check_if_username_unique(
        self,
        request: UnicornRequest,
        res: Response,
        username: str,
    ) -> ResponseModel[bool]:
        try:
            username_status = await self.userService.check_if_username_exist_and_fail(
                username, True
            )

            return self.responseService.send_response(
                res, status.HTTP_200_OK, "username available", username_status
            )
        except Exception as e:
            return self.responseService.send_response(
                res,
                status.HTTP_400_BAD_REQUEST,
                f"{str(e)}",
            )
