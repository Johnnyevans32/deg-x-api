# -*- coding: utf-8 -*-
from typing import Sequence

from fastapi import Depends, Response, status
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from apps.auth.services.auth_bearer import JWTBearer
from apps.blockchain.interfaces.transaction_interface import BlockchainTransactionOut
from apps.blockchain.services.blockchain_service import (
    BlockchainService,
)
from apps.blockchain.types.blockchain_type import (
    SendTokenDTO,
    SendTxnRes,
    GetTokenBalance,
    BalanceRes,
    GetTestTokenDTO,
    SwapTokenDTO,
)
from core.middleware.encryption import DecrptRequestRoute
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseModel, ResponseService

router = InferringRouter(
    prefix="/blockchain", tags=["Blockchain 💸"], route_class=DecrptRequestRoute
)


@cbv(router)
class BlockchainController:
    blockchainService = BlockchainService()
    responseService = ResponseService()

    @router.get(
        "/get-transaction",
        dependencies=[Depends(JWTBearer())],
        response_model_by_alias=False,
    )
    async def get_blockchain_txn(
        self,
        request: UnicornRequest,
        response: Response,
        page_num: int = 1,
        page_size: int = 10,
    ) -> ResponseModel[Sequence[BlockchainTransactionOut]]:
        try:
            user = request.state.user
            request.app.logger.info(f"getting user blockchain transactions - {user.id}")
            user_txns, meta_data = await self.blockchainService.get_transactions(
                user, page_num, page_size
            )
            request.app.logger.info("done getting user blockchain transction data ")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "user blockchain transction data retrieved",
                user_txns,
                meta_data,
            )

        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in getting user blockchain transction data: {str(e)}",
            )

    @router.post("/send-token", dependencies=[Depends(JWTBearer())])
    async def send_token(
        self, request: UnicornRequest, response: Response, payload: SendTokenDTO
    ) -> ResponseModel[SendTxnRes]:
        try:
            user = request.state.user
            request.app.logger.info(f"sending blockchain token for - {user.id}")
            user_txn = await self.blockchainService.send(user, payload)
            request.app.logger.info("done sending blockchain token")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "token successfully sent",
                user_txn,
            )

        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in sending blockchain token - {str(e)}",
            )

    @router.post(
        "/get-token-balance",
        dependencies=[Depends(JWTBearer())],
    )
    async def get_token_balance(
        self, request: UnicornRequest, response: Response, payload: GetTokenBalance
    ) -> ResponseModel[BalanceRes]:
        try:
            user = request.state.user
            request.app.logger.info(f"getting token balance for - {user.id}")
            user_token_balance = await self.blockchainService.get_balance(user, payload)
            request.app.logger.info("done getting token balance")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "token balance retrieved successfully",
                user_token_balance,
            )

        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in getting token balance - {str(e)}",
            )

    @router.post(
        "/chain-swap",
        dependencies=[Depends(JWTBearer())],
    )
    async def swap_between_wraps(
        self, request: UnicornRequest, response: Response, payload: SwapTokenDTO
    ) -> ResponseModel[str]:
        try:
            user = request.state.user
            request.app.logger.info(
                f"swapping tokens between wraps for user - {user.id}"
            )
            swap_txn = await self.blockchainService.swap_between_wraps(user, payload)
            request.app.logger.info("done swapping tokens between wraps")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "successful swapping tokens between wraps",
                swap_txn,
            )

        except Exception as e:
            # raise e
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in swapping tokens between wraps - {str(e)}",
            )

    @router.post(
        "/get-test-token",
        dependencies=[Depends(JWTBearer())],
    )
    async def get_test_token(
        self, request: UnicornRequest, response: Response, payload: GetTestTokenDTO
    ) -> ResponseModel[SendTxnRes]:
        try:
            user = request.state.user
            request.app.logger.info("sending airdrop token balance ")
            txn_res = await self.blockchainService.get_test_token(user, payload)
            request.app.logger.info("done sending airdrop token balance to address")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "airdrop token balance sent",
                txn_res,
            )

        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in sending airdrop token balance - {str(e)}",
            )
