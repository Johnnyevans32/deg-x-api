# -*- coding: utf-8 -*-
from fastapi import Depends, Response, status
from fastapi.routing import APIRouter

from apps.auth.services.auth_bearer import JWTBearer
from apps.blockchain.interfaces.transaction_interface import BlockchainTransactionOut
from apps.blockchain.services.blockchain_service import (
    BlockchainService,
    GetTokenBalance,
    SendTokenDTO,
)
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseService, get_response_model

router = APIRouter(prefix="/api/v1/blockchain", tags=["Blockchain 💸"])


blockchainService = BlockchainService()
responseService = ResponseService()


@router.get(
    "/get-transaction",
    dependencies=[Depends(JWTBearer())],
    response_model=get_response_model(
        list[BlockchainTransactionOut], "BlockchainTransactionOutResponse"
    ),
)
async def get_blockchain_txn(
    request: UnicornRequest,
    response: Response,
    page_num: int = 1,
    page_size: int = 10,
):
    try:
        user = request.state.user
        request.app.logger.info(f"getting user blockchain transactions - {user.id}")
        user_txns, meta_data = await blockchainService.get_transactions(
            user, page_num, page_size
        )
        request.app.logger.info("done getting user blockchain transction data ")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "user blockchain transction data retrieved",
            user_txns,
            meta_data,
        )

    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in getting user blockchain transction data: {str(e)}",
        )


@router.post(
    "/send-token",
    dependencies=[Depends(JWTBearer())],
    # response_model=get_response_model(
    #     list[BlockchainTransactionOut], "BlockchainTransactionOutResponse"
    # ),
)
async def send_token(
    request: UnicornRequest, response: Response, payload: SendTokenDTO
):
    try:
        user = request.state.user
        request.app.logger.info(f"sending blockchain token for - {user.id}")
        user_txn = await blockchainService.send(user, payload)
        request.app.logger.info("done sending blockchain token")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "token successfully sent",
            user_txn,
        )

    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in sending blockchain token - {str(e)}",
        )


@router.post(
    "/get-token-balance",
    dependencies=[Depends(JWTBearer())],
    # response_model=get_response_model(
    #     list[BlockchainTransactionOut], "BlockchainTransactionOutResponse"
    # ),
)
async def get_token_balance(
    request: UnicornRequest, response: Response, payload: GetTokenBalance
):
    try:
        user = request.state.user
        request.app.logger.info(f"getting token balance for - {user.id}")
        user_token_balance = await blockchainService.get_balance(user, payload)
        request.app.logger.info("done getting token balance")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "token balance retrieved successfully",
            user_token_balance,
        )

    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in getting token balance - {str(e)}",
        )
