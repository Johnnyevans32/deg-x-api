# -*- coding: utf-8 -*-
from fastapi import Depends, Response, status
from fastapi.routing import APIRouter

from apps.auth.services.auth_bearer import JWTBearer
from apps.wallet.services.wallet_service import WalletService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseService

# from apps.wallet.interfaces.walletasset_interface import WalletAsset


router = APIRouter(prefix="/api/v1/wallet", tags=["Wallet 💸"])


walletService = WalletService()
responseService = ResponseService()


@router.get(
    "/retrieve-wallet",
    dependencies=[Depends(JWTBearer())],
    # response_model=get_response_model(list[WalletAsset], "WalletAssetResponse"),
)
async def retrieve_wallet_assets(request: UnicornRequest, response: Response):
    try:
        if hasattr(request.state, "error"):
            raise request.state.error
        user = request.state.user
        request.state
        request.app.logger.info(f"checking wallet for - {user.id}")
        user_walletassets = walletService.retrieve_wallet_assets(user)
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
