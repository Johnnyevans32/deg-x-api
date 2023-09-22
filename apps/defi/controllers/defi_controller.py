# -*- coding: utf-8 -*-
from typing import Sequence

from fastapi import Response, status, APIRouter
from fastapi_restful.cbv import cbv

from apps.auth.services.auth_bearer import CurrentUser
from apps.defi.interfaces.defiprovider_interface import DefiProviderOut
from apps.defi.services.defi_service import DefiService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseModel, ResponseService

router = APIRouter(prefix="/defi", tags=["Defi 💸"])


@cbv(router)
class DefiController:
    defiService = DefiService()
    responseService = ResponseService()

    @router.get(
        "/providers",
        response_model_by_alias=False,
    )
    async def get_defi_providers_by_default_network(
        self,
        request: UnicornRequest,
        response: Response,
        user: CurrentUser,
    ) -> ResponseModel[Sequence[DefiProviderOut]]:
        try:
            request.app.logger.info(
                f"retrieving defi providers for networks for user - {user.id}"
            )
            defi_providers = (
                await self.defiService.get_defi_providers_by_default_network(user)
            )
            request.app.logger.info(
                f"done retrieving defi providers for networks for user - {user.id}"
            )
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "defi providers for networks retrieved",
                defi_providers,
            )

        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in retrieving defi providers for networks: {str(e)}",
            )
