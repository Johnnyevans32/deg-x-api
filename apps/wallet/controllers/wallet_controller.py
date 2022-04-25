# -*- coding: utf-8 -*-
from calendar import c
from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter

from apps.auth.services.auth_bearer import JWTBearer
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from apps.wallet.services.wallet_service import WalletService
from core.utils.response_service import ResponseService, get_response_model

router = APIRouter(prefix="/api/v1/wallet", tags=["Wallet 💸"])


walletService = WalletService()
responseService = ResponseService()


@router.get(
    "/retrieve-wallet",
    dependencies=[Depends(JWTBearer())],
    response_model=get_response_model(Wallet, "WalletResponse"),
)
async def retrieve_wallet(self, request: Request, response: Response):
    try:
        if hasattr(request.state, "error"):
            raise request.state.error
        user: User = request.state.user
        request.app.logger.info(f"checking wallet for - {user.id}")
        user_wallet = self.walletService.retrieve_wallet(user)
        request.app.logger.info("done retrieving wallet")
        return self.responseService.send_response(
            response, status.HTTP_200_OK, "user balance retrieved", user_wallet
        )

    except Exception as e:
        return self.responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in getting user wallet: {str(e)}",
        )
