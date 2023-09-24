# -*- coding: utf-8 -*-
from fastapi import Response, status, APIRouter
from fastapi_restful.cbv import cbv

from apps.auth.services.auth_bearer import CurrentUser
from apps.user.interfaces.user_interface import UserUpdateDTO
from apps.user.services.user_service import UserService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseModel, ResponseService

router = APIRouter(prefix="/users", tags=["User 🌈"])


@cbv(router)
class UserController:
    userService = UserService()
    responseService = ResponseService()

    @router.put(
        "/",
        response_model_by_alias=False,
    )
    async def update_user_profile(
        self,
        request: UnicornRequest,
        res: Response,
        user: CurrentUser,
        update_payload: UserUpdateDTO,
    ) -> ResponseModel[None]:
        try:
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
        response_model_by_alias=False,
    )
    async def check_if_username_unique(
        self,
        request: UnicornRequest,
        res: Response,
        user: CurrentUser,
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
