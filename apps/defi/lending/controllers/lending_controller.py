# -*- coding: utf-8 -*-
from fastapi import Depends, Response, status
from fastapi.routing import APIRouter
from apps.auth.services.auth_bearer import JWTBearer
from apps.defi.lending.services.lending_service import LendingService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseService

router = APIRouter(prefix="/api/v1/defi/lending", tags=["Lending 💸"])


lendingService = LendingService()
responseService = ResponseService()


@router.get(
    "/get-user-account-data",
    dependencies=[Depends(JWTBearer())],
    # response_model=get_response_model(list[WalletAsset], "WalletResponse"),
)
async def get_user_account_data(request: UnicornRequest, response: Response):
    try:
        if hasattr(request.state, "error"):
            raise request.state.error
        user = request.state.user
        request.app.logger.info(f"getting user lending pool data for - {user.id}")
        user_lending_data = lendingService.get_user_lending_data(user)
        request.app.logger.info("done getting user lending pool data ")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "user lending account data retrieved",
            user_lending_data,
        )

    except Exception as e:
        # raise e
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in getting user lending account data: {str(e)}",
        )


@router.get(
    "/get-user-config",
    dependencies=[Depends(JWTBearer())],
    # response_model=get_response_model(list[WalletAsset], "WalletResponse"),
)
async def get_user_config(request: UnicornRequest, response: Response):
    try:
        if hasattr(request.state, "error"):
            raise request.state.error
        user = request.state.user
        request.app.logger.info(f"getting user lending pool data for - {user.id}")
        user_lending_data = lendingService.get_user_config(user)
        request.app.logger.info("done getting user lending pool data ")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "user lending account data retrieved",
            user_lending_data,
        )

    except Exception as e:
        # raise e
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in getting user lending account data: {str(e)}",
        )
