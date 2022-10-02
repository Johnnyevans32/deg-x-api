# -*- coding: utf-8 -*-
from fastapi import Response, status, Depends
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from apps.auth.services.auth_bearer import JWTBearer
from apps.user.interfaces.user_interface import UserUpdateDTO
from apps.user.services.user_service import UserService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseModel, ResponseService

router = InferringRouter(prefix="/user", tags=["User 🌈"])


@cbv(router)
class UserController:
    userService = UserService()
    responseService = ResponseService()

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
                res, status.HTTP_200_OK, "feature status updated successfully"
            )
        except Exception as e:
            request.app.logger.error(f"Error updating user profile- {str(e)}")
            return self.responseService.send_response(
                res,
                status.HTTP_400_BAD_REQUEST,
                f"Error updating user profile {str(e)}",
            )
