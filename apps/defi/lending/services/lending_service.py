from typing import Any, Optional, cast
from apps.blockchain.interfaces.blockchain_interface import Blockchain

from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.blockchain.services.blockchain_service import BlockchainService
from apps.defi.interfaces.defiprovider_interface import DefiProvider, DefiServiceType
from apps.defi.lending.types.lending_types import IReserveTokens, IUserAcccountData
from apps.defi.lending.interfaces.lending_request_interface import (
    InterestRateMode,
    LendingRequest,
    LendingRequestStatus,
    LendingRequestType,
)
from apps.defi.lending.registry.lending_registry import LendingRegistry
from apps.defi.lending.types.lending_types import BaseLendingActionDTO, BorrowAssetDTO
from apps.notification.slack.services.slack_service import SlackService
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from apps.wallet.interfaces.walletasset_interface import WalletAsset
from apps.wallet.services.wallet_service import WalletService
from core.depends.get_object_id import PyObjectId
from core.utils.model_utility_service import ModelUtilityService
from core.utils.response_service import MetaDataModel


class LendingService:
    walletService = WalletService()
    lendingRegistry = LendingRegistry()
    slackService = SlackService()

    @staticmethod
    async def get_default_provider_key() -> DefiProvider:
        default_lending_provider = await ModelUtilityService.find_one_and_populate(
            DefiProvider,
            {
                "isDefault": True,
                "serviceType": DefiServiceType.LENDING,
                "isDeleted": False,
            },
            ["network", "blockchain"],
        )

        if not default_lending_provider:
            raise Exception("no default lending provider set")

        return default_lending_provider

    async def get_defi_provider(
        self, defi_provider_id: PyObjectId | None
    ) -> DefiProvider:
        if not defi_provider_id:
            return await self.get_default_provider_key()

        defi_provider = await ModelUtilityService.find_one_and_populate(
            DefiProvider, {"_id": defi_provider_id}, ["network", "blockchain"]
        )
        if not defi_provider:
            raise Exception("defi protocol not found")

        return defi_provider

    async def get_wallet_asset(
        self, user: User, user_wallet: Wallet, defi_provider: DefiProvider
    ) -> WalletAsset:
        blockchain = cast(Blockchain, defi_provider.blockchain)
        user_wallet_asset = await ModelUtilityService.find_one(
            WalletAsset,
            {
                "wallet": user_wallet.id,
                "user": user.id,
                "blockchain": blockchain.id,
                "isDeleted": False,
            },
        )
        if not user_wallet_asset:
            raise Exception("user asset not found")

        return user_wallet_asset

    async def get_user_lending_requests(
        self,
        user: User,
        page_num: int,
        page_size: int,
        defi_provider: PyObjectId = None,
    ) -> tuple[list[LendingRequest], MetaDataModel]:

        user_wallet = await self.walletService.get_user_default_wallet(user)
        query = {"wallet": user_wallet.id, "isDeleted": False}
        if not defi_provider:
            query["defiProvider"] = defi_provider
        lending_reqs, metadata = await ModelUtilityService.populate_and_paginate_data(
            LendingRequest,
            {"wallet": user_wallet.id, "isDeleted": False},
            ["defiProvider"],
            page_num,
            page_size,
        )
        return lending_reqs, metadata

    async def get_user_lending_data(
        self,
        user: User,
        defi_provider_id: PyObjectId = None,
    ) -> IUserAcccountData:
        defi_provider = await self.get_defi_provider(defi_provider_id)
        user_wallet = await self.walletService.get_user_default_wallet(user)
        user_wallet_asset = await self.get_wallet_asset(
            user, user_wallet, defi_provider
        )
        user_lending_data = await self.lendingRegistry.get_service(
            defi_provider.serviceName
        ).get_user_account_data(user_wallet_asset.address, defi_provider)

        return user_lending_data

    async def get_reserve_assets(
        self,
        defi_provider_id: PyObjectId = None,
    ) -> list[IReserveTokens]:
        defi_provider = await self.get_defi_provider(defi_provider_id)
        reserve_assets = await self.lendingRegistry.get_service(
            defi_provider.serviceName
        ).get_reserve_assets(defi_provider)

        return reserve_assets

    async def get_user_config(
        self,
        user: User,
        defi_provider_id: PyObjectId = None,
    ) -> Any:
        defi_provider = await self.get_defi_provider(defi_provider_id)
        user_wallet = await self.walletService.get_user_default_wallet(user)
        user_wallet_asset = await self.get_wallet_asset(
            user, user_wallet, defi_provider
        )
        user_config_data = await self.lendingRegistry.get_service(
            defi_provider.serviceName
        ).get_user_config(user_wallet_asset.address, defi_provider)

        return user_config_data

    async def borrow(
        self,
        user: User,
        payload: BorrowAssetDTO,
    ) -> LendingRequest:
        defi_provider = await self.get_defi_provider(payload.provider)
        user_wallet = await self.walletService.get_user_default_wallet(user)
        user_wallet_asset = await self.get_wallet_asset(
            user, user_wallet, defi_provider
        )
        protocol_borrow_res = await self.lendingRegistry.get_service(
            defi_provider.serviceName
        ).borrow(
            payload.asset,
            payload.amount,
            payload.interestRateMode,
            user_wallet_asset.address,
            defi_provider,
            user_wallet.mnemonic or payload.mnemonic,
        )
        token_asset = await BlockchainService.get_token_asset_by_query(
            {"contractAddress": payload.asset}
        )

        lending_req = await self.create_lending_request(
            user,
            user_wallet,
            LendingRequestType.BORROW,
            defi_provider,
            token_asset,
            protocol_borrow_res,
            payload.amount,
            payload.asset,
            payload.interestRateMode,
        )

        return lending_req

    async def create_lending_request(
        self,
        user: User,
        user_wallet: Wallet,
        lending_type: LendingRequestType,
        defi_provider: DefiProvider,
        token_asset: Optional[TokenAsset],
        provider_res: str,
        amount: float,
        asset: str,
        interest_rate_mode: InterestRateMode = None,
    ) -> LendingRequest:
        lending_req = await ModelUtilityService.model_create(
            LendingRequest,
            LendingRequest(
                user=cast(PyObjectId, user.id),
                wallet=cast(PyObjectId, user_wallet.id),
                amount=amount,
                interestRateMode=interest_rate_mode,
                defiProvider=cast(PyObjectId, defi_provider.id),
                requestType=lending_type,
                status=LendingRequestStatus.OPEN,
                tokenAsset=(cast(PyObjectId, token_asset.id) if token_asset else asset),
                providerResponse=provider_res,
            ).dict(by_alias=True, exclude_none=True),
        )
        return lending_req

    async def deposit(
        self,
        user: User,
        payload: BaseLendingActionDTO,
    ) -> LendingRequest:
        defi_provider = await self.get_defi_provider(payload.provider)
        user_wallet = await self.walletService.get_user_default_wallet(user)
        user_wallet_asset = await self.get_wallet_asset(
            user, user_wallet, defi_provider
        )
        try:
            protocol_deposit_res = await self.lendingRegistry.get_service(
                defi_provider.serviceName
            ).deposit(
                payload.asset,
                payload.amount,
                user_wallet_asset.address,
                defi_provider,
                user_wallet.mnemonic or payload.mnemonic,
            )
        except Exception as e:
            self.slackService.send_formatted_message(
                "Error from lending defi provider",
                f"An error just occured from {defi_provider.serviceName} "
                f"lending provider \n *Error:* ```{e}```",
                "error-report",
            )
            raise e
        token_asset = await ModelUtilityService.find_one(
            TokenAsset, {"contractAddress": payload.asset, "isDeleted": False}
        )
        lending_req = await self.create_lending_request(
            user,
            user_wallet,
            LendingRequestType.DEPOSIT,
            defi_provider,
            token_asset,
            protocol_deposit_res,
            payload.amount,
            payload.asset,
        )
        return lending_req

    async def repay(
        self,
        user: User,
        payload: BorrowAssetDTO,
    ) -> LendingRequest:
        defi_provider = await self.get_defi_provider(payload.provider)
        user_wallet = await self.walletService.get_user_default_wallet(user)
        user_wallet_asset = await self.get_wallet_asset(
            user, user_wallet, defi_provider
        )
        protocol_repay_res = await self.lendingRegistry.get_service(
            defi_provider.serviceName
        ).repay(
            payload.asset,
            payload.amount,
            payload.interestRateMode,
            user_wallet_asset.address,
            defi_provider,
            user_wallet.mnemonic or payload.mnemonic,
        )
        token_asset = await BlockchainService.get_token_asset_by_query(
            {"contractAddress": payload.asset}
        )
        lending_req = await self.create_lending_request(
            user,
            user_wallet,
            LendingRequestType.REPAY,
            defi_provider,
            token_asset,
            protocol_repay_res,
            payload.amount,
            payload.asset,
            payload.interestRateMode,
        )
        return lending_req
