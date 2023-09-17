# -*- coding: utf-8 -*-
from typing import Sequence

from fastapi import Depends, Response, status, APIRouter
from fastapi_restful.cbv import cbv

from apps.auth.interfaces.auth_interface import AuthResponse
from apps.auth.services.auth_bearer import JWTBearer
from apps.blockchain.interfaces.network_interface import NetworkType
from apps.blockchain.interfaces.tokenasset_interface import TokenAssetCore
from apps.wallet.interfaces.wallet_interface import WalletOut
from apps.wallet.interfaces.walletasset_interface import WalletAssetOut
from apps.wallet.services.wallet_service import WalletService
from core.depends.get_object_id import PyObjectId
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseModel, ResponseService

router = APIRouter(prefix="/wallet", tags=["Wallet 💸"])


@cbv(router)
class WalletController:
    walletService = WalletService()
    responseService = ResponseService()

    @router.get(
        "/assets",
        dependencies=[Depends(JWTBearer())],
        response_model_by_alias=False,
    )
    async def retrieve_wallet_assets(
        self, request: UnicornRequest, response: Response
    ) -> ResponseModel[Sequence[WalletAssetOut]]:
        try:
            user = request.state.user
            request.app.logger.info(f"checking wallet for - {user.id}")
            user_walletassets = await self.walletService.retrieve_wallet_assets(user)
            request.app.logger.info("done retrieving wallet assets")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "user wallet assets retrieved",
                user_walletassets,
            )
        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in getting user wallet assets: {str(e)}",
            )

    @router.post(
        "/",
        dependencies=[Depends(JWTBearer())],
        response_model_by_alias=False,
    )
    async def create_user_wallet(
        self, request: UnicornRequest, response: Response
    ) -> ResponseModel[AuthResponse]:
        try:
            user = request.state.user
            request.app.logger.info(f"creating wallet for - {user.id}")
            user_wallet, seed = await self.walletService.create_wallet(user)
            request.app.logger.info("done creating user wallet")
            return self.responseService.send_response(
                response,
                status.HTTP_201_CREATED,
                "user wallet created successfully",
                AuthResponse(wallet=user_wallet, seed=seed),
            )
        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in creating user wallet: {str(e)}",
            )

    @router.get(
        "/",
        dependencies=[Depends(JWTBearer())],
        response_model_by_alias=False,
    )
    async def retrieve_wallets(
        self, request: UnicornRequest, response: Response
    ) -> ResponseModel[Sequence[WalletOut]]:
        try:
            user = request.state.user
            request.app.logger.info(f"retrieving user wallets for - {user.id}")
            user_wallets = await self.walletService.retrieve_user_wallets(user)
            request.app.logger.info("done retrieving user wallets")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "user wallets retrieved",
                user_wallets,
            )
        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in getting user wallets: {str(e)}",
            )

    @router.put(
        "/set-wallet-network-type",
        dependencies=[Depends(JWTBearer())],
    )
    async def switch_wallet_network(
        self, request: UnicornRequest, response: Response, network_type: NetworkType
    ) -> ResponseModel[None]:
        try:
            user = request.state.user
            request.app.logger.info(f"setting user wallet network for - {user.id}")
            await self.walletService.update_wallet_network(user, network_type)
            request.app.logger.info("done setting user wallet network")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "user wallet network type updated successfully",
            )
        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in setting user wallet network: {str(e)}",
            )

    @router.put(
        "/set-default-user-wallet",
        dependencies=[Depends(JWTBearer())],
    )
    async def switch_default_wallet(
        self, request: UnicornRequest, response: Response, wallet_id: PyObjectId
    ) -> ResponseModel[None]:
        try:
            user = request.state.user
            request.app.logger.info(f"setting user default wallet for - {user.id}")
            await self.walletService.update_dafault_wallet(user, wallet_id)
            request.app.logger.info("done setting user default wallet")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "user default wallet updated successfully",
            )
        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in setting user default wallet: {str(e)}",
            )

    @router.post(
        "/token",
        dependencies=[Depends(JWTBearer())],
        response_model_by_alias=False,
    )
    async def add_wallet_address(
        self, request: UnicornRequest, response: Response, payload: TokenAssetCore
    ) -> ResponseModel[WalletAssetOut]:
        try:
            user = request.state.user
            asset = await self.walletService.add_token_asset(user, payload)
            return self.responseService.send_response(
                response,
                status.HTTP_201_CREATED,
                "user wallet asset added successfully",
                asset,
            )
        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in adding user wallet asset: {str(e)}",
            )
