# -*- coding: utf-8 -*-
from fastapi import Depends, Response, status
from fastapi.routing import APIRouter

from apps.auth.services.auth_bearer import JWTBearer
from apps.defi.lending.services.lending_service import LendingService
from apps.defi.lending.types.lending_types import BorrowAssetDTO, DepositAssetDTO
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
        raise e
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


@router.post(
    "/deposit",
    dependencies=[Depends(JWTBearer())],
    # response_model=get_response_model(list[WalletAsset], "WalletResponse"),
)
async def deposit_asset(
    request: UnicornRequest, response: Response, payload: DepositAssetDTO
):
    try:
        if hasattr(request.state, "error"):
            raise request.state.error
        user = request.state.user
        request.app.logger.info(f"initiating deposit request to protocol - {user.id}")
        borrow_asset_res = lendingService.deposit(user, payload)
        request.app.logger.info("done initiating deposit request to protocol ")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "asset deposit to protocol successfully",
            borrow_asset_res,
        )

    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in initiating deposit request to protocol: {str(e)}",
        )


@router.post(
    "/borrow",
    dependencies=[Depends(JWTBearer())],
    # response_model=get_response_model(list[WalletAsset], "WalletResponse"),
)
async def borrrow_asset(
    request: UnicornRequest, response: Response, payload: BorrowAssetDTO
):
    try:
        if hasattr(request.state, "error"):
            raise request.state.error
        user = request.state.user
        request.app.logger.info(f"initiating borrow request to protocol - {user.id}")
        borrow_asset_res = lendingService.borrow(user, payload)
        request.app.logger.info("done initiating borrow request to protocol ")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "asset borrowed to wallet successfully",
            borrow_asset_res,
        )

    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in initiating borrow request to protocol: {str(e)}",
        )


@router.post(
    "/repay",
    dependencies=[Depends(JWTBearer())],
    # response_model=get_response_model(list[WalletAsset], "WalletResponse"),
)
async def repay_asset(
    request: UnicornRequest, response: Response, payload: BorrowAssetDTO
):
    try:
        if hasattr(request.state, "error"):
            raise request.state.error
        user = request.state.user
        request.app.logger.info(f"initiating repaid request to protocol - {user.id}")
        borrow_asset_res = lendingService.repay(user, payload)
        request.app.logger.info("done initiating repaid request to protocol ")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "asset repaid to protocol successfully",
            borrow_asset_res,
        )

    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in initiating repay request to protocol: {str(e)}",
        )


@router.get(
    "/reserved-assets",
    # response_model=get_response_model(list[WalletAsset], "WalletResponse"),
)
async def get_reserved_assets(request: UnicornRequest, response: Response):
    try:
        request.app.logger.info("getting reserved assets from protocol")
        reserved_assets_res = lendingService.get_reserved_assets()
        request.app.logger.info("done getting reserved assets from protocol")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "reserved assets retrieved successfully",
            reserved_assets_res,
        )

    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in getting reserved assets from protocol: {str(e)}",
        )
