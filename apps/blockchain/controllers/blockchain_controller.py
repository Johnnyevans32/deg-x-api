# -*- coding: utf-8 -*-
from fastapi import Depends, Response, status
from fastapi.routing import APIRouter

from apps.auth.services.auth_bearer import JWTBearer
from apps.blockchain.services.blockchain_service import BlockchainService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseService

router = APIRouter(prefix="/api/v1/blockchain", tags=["Blockchain 💸"])


blockchainService = BlockchainService()
responseService = ResponseService()


@router.get(
    "/get-transaction",
    dependencies=[Depends(JWTBearer())],
    # response_model=get_response_model(list[WalletAsset], "WalletResponse"),
)
async def get_blockchain_txn(
    request: UnicornRequest,
    response: Response,
    page_num: int = 1,
    page_size: int = 10,
):
    try:
        if hasattr(request.state, "error"):
            raise request.state.error
        user = request.state.user
        request.app.logger.info(f"getting user blockchain transactions - {user.id}")
        user_txns = await blockchainService.get_transactions(user, page_num, page_size)
        request.app.logger.info("done getting user blockchain transction data ")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "user blockchain transction data retrieved",
            user_txns,
        )

    except Exception as e:
        raise e
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in getting user blockchain transction data: {str(e)}",
        )
