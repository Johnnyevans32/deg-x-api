# -*- coding: utf-8 -*-
from fastapi import Depends, Response, status
from fastapi.routing import APIRouter
from apps.auth.services.auth_bearer import JWTBearer
from apps.defi.interfaces.defi_provider_interface import DefiProviderOut

from apps.defi.services.defi_service import DefiService

from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseService, get_response_model

router = APIRouter(prefix="/api/v1/defi", tags=["Defi 💸"])


defiService = DefiService()
responseService = ResponseService()


@router.get(
    "/get-defi-providers",
    dependencies=[Depends(JWTBearer())],
    response_model=get_response_model(list[DefiProviderOut], "DefiProviderResponse"),
)
async def get_defi_providers_by_default_network(
    request: UnicornRequest,
    response: Response,
):
    try:
        user = request.state.user
        request.app.logger.info(
            f"retrieving defi providers for networks for user - {user.id}"
        )
        defi_providers = await defiService.get_defi_providers_by_default_network(user)
        request.app.logger.info(
            f"done retrieving defi providers for networks for user - {user.id}"
        )
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "defi providers for networks retrieved",
            defi_providers,
        )

    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in retrieving defi providers for networks: {str(e)}",
        )
