# -*- coding: utf-8 -*-
from fastapi import Depends, Response, status
from fastapi.routing import APIRouter

from apps.auth.services.auth_bearer import JWTBearer
from apps.blockchain.interfaces.network_interface import NetworkType
from apps.wallet.interfaces.wallet_interface import WalletOut
from apps.wallet.interfaces.walletasset_interface import WalletAssetOut
from apps.wallet.services.wallet_service import WalletService

from core.depends.get_object_id import PyObjectId
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseService, get_response_model


router = APIRouter(prefix="/api/v1/wallet", tags=["Wallet 💸"])


walletService = WalletService()
responseService = ResponseService()


@router.get(
    "/retrieve-wallet-assets",
    dependencies=[Depends(JWTBearer())],
    response_model_by_alias=False,
    response_model=get_response_model(list[WalletAssetOut], "WalletAssetResponse"),
)
async def retrieve_wallet_assets(request: UnicornRequest, response: Response):
    try:
        user = request.state.user
        request.app.logger.info(f"checking wallet for - {user.id}")
        user_walletassets = await walletService.retrieve_wallet_assets(user)
        request.app.logger.info("done retrieving wallet assets")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "user wallet assets retrieved",
            user_walletassets,
        )
    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in getting user wallet assets: {str(e)}",
        )


@router.post(
    "/create",
    dependencies=[Depends(JWTBearer())],
    response_model_by_alias=False,
    response_model=get_response_model(WalletOut, "CreateWalletResponse"),
)
async def create_user_wallet(request: UnicornRequest, response: Response):
    try:
        user = request.state.user
        request.app.logger.info(f"creating wallet for - {user.id}")
        user_wallet = await walletService.create_wallet(user)
        request.app.logger.info("done creating user wallet")
        return responseService.send_response(
            response,
            status.HTTP_201_CREATED,
            "user wallet created successfully",
            user_wallet,
        )
    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in creating user wallet: {str(e)}",
        )


@router.get(
    "/retrieve-wallets",
    dependencies=[Depends(JWTBearer())],
    response_model_by_alias=False,
    response_model=get_response_model(list[WalletOut], "WalletResponse"),
)
async def retrieve_wallets(request: UnicornRequest, response: Response):
    try:
        user = request.state.user
        request.app.logger.info(f"retrieving user wallets for - {user.id}")
        user_wallets = await walletService.retrieve_user_wallets(user)
        request.app.logger.info("done retrieving user wallets")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "user wallets retrieved",
            user_wallets,
        )
    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in getting user wallets: {str(e)}",
        )


@router.patch(
    "/set-wallet-network-type",
    dependencies=[Depends(JWTBearer())],
)
async def switch_wallet_network(
    request: UnicornRequest, response: Response, network_type: NetworkType
):
    try:
        user = request.state.user
        request.app.logger.info(f"setting user wallet network for - {user.id}")
        await walletService.update_wallet_network(user, network_type)
        request.app.logger.info("done setting user wallet network")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "user wallet network type updated successfully",
        )
    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in setting user wallet network: {str(e)}",
        )


@router.patch(
    "/set-default-user-wallet",
    dependencies=[Depends(JWTBearer())],
)
async def switch_default_wallet(
    request: UnicornRequest, response: Response, wallet_id: PyObjectId
):
    try:
        user = request.state.user
        request.app.logger.info(f"setting user default wallet for - {user.id}")
        await walletService.update_dafault_wallet(user, wallet_id)
        request.app.logger.info("done setting user default wallet")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "user default wallet updated successfully",
        )
    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in setting user default wallet: {str(e)}",
        )
