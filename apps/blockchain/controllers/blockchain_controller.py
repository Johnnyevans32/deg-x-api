# -*- coding: utf-8 -*-
from fastapi import Depends, Response, status
from fastapi.routing import APIRouter

from apps.auth.services.auth_bearer import JWTBearer
from apps.blockchain.interfaces.transaction_interface import BlockchainTransactionOut
from apps.blockchain.services.blockchain_service import (
    BlockchainService,
    GetTokenBalance,
    SendTokenDTO,
    SwapTokenDTO,
)
from apps.blockchain.solana.solana_service import SolanaService

from apps.blockchain.tezos.tezos_service import TezosService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseService, get_response_model

router = APIRouter(prefix="/api/v1/blockchain", tags=["Blockchain 💸"])

blockchainService = BlockchainService()
responseService = ResponseService()
solanaService = SolanaService()
tezosService = TezosService()


@router.get(
    "/get-transaction",
    dependencies=[Depends(JWTBearer())],
    response_model_by_alias=False,
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
        raise e
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
        raise e
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in getting token balance - {str(e)}",
        )


@router.post(
    "/chain-swap",
    dependencies=[Depends(JWTBearer())],
)
async def swap_between_wraps(
    request: UnicornRequest, response: Response, payload: SwapTokenDTO
):
    try:
        user = request.state.user
        request.app.logger.info(f"swapping tokens between wraps for user - {user.id}")
        swap_txn = await blockchainService.swap_between_wraps(user, payload)
        request.app.logger.info("done swapping tokens between wraps")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "successful swapping tokens between wraps",
            swap_txn,
        )

    except Exception as e:
        # raise e
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in swapping tokens between wraps - {str(e)}",
        )


@router.post(
    "/fund-solana-account-devnet",
)
async def fund_my_solana_account(
    request: UnicornRequest, response: Response, payload: SendTokenDTO
):
    try:
        request.app.logger.info(
            f"sending airdrop token balance to address - {payload.toAddress}"
        )
        user_token_balance = await solanaService.get_test_token(
            payload.toAddress, int(payload.amount)
        )
        request.app.logger.info("done sending airdrop token balance to address")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "airdrop token balance sent",
            user_token_balance,
        )

    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in sending airdrop token balance - {str(e)}",
        )


@router.post(
    "/fund-tezos-account-devnet",
)
async def fund_my_tezos_account(
    request: UnicornRequest, response: Response, payload: SendTokenDTO
):
    try:
        request.app.logger.info(
            f"sending airdrop token balance to address - {payload.toAddress}"
        )
        user_token_balance = await tezosService.fund_tezos_wallet(
            payload.toAddress, int(payload.amount)
        )
        request.app.logger.info("done sending airdrop token balance to address")
        return responseService.send_response(
            response,
            status.HTTP_200_OK,
            "airdrop token balance sent",
            user_token_balance,
        )

    except Exception as e:
        raise e
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in sending airdrop token balance - {str(e)}",
        )
