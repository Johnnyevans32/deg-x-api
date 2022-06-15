import eth_utils

from apps.blockchain.services.blockchain_service import BlockchainService
from apps.defi.interfaces.defi_provider_interface import DefiProvider, DefiServiceType
from apps.defi.lending.interfaces.lending_request_interface import (
    LendingRequest,
    LendingRequestStatus,
    LendingRequestType,
)
from apps.defi.lending.services.lending_registry import LendingRegistry
from apps.defi.lending.types.lending_types import BorrowAssetDTO, DepositAssetDTO
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from apps.wallet.interfaces.walletasset_interface import WalletAsset
from apps.wallet.services.wallet_service import WalletService
from core.depends.get_object_id import PyObjectId
from core.utils.model_utility_service import ModelUtilityService

# from apps.user.interfaces.user_interface import User


class LendingService:
    walletService = WalletService()
    lendingRegistry = LendingRegistry()

    @staticmethod
    def get_default_provider_key() -> DefiProvider:
        default_lending_provider = ModelUtilityService.find_one_and_populate(
            DefiProvider,
            {
                "isDefault": True,
                "serviceType": DefiServiceType.LENDING,
                "isDeleted": False,
            },
            ["network"],
        )

        if default_lending_provider is None:
            raise Exception("no default lending provider set")

        return default_lending_provider

    def get_defi_provider(self, defi_provider_id: PyObjectId | None) -> DefiProvider:
        if defi_provider_id is None:
            return LendingService.get_default_provider_key()

        defi_provider = ModelUtilityService.find_one_and_populate(
            DefiProvider, {"_id": defi_provider_id}, ["network"]
        )
        if defi_provider is None:
            raise Exception("defi protocol not found")

        return defi_provider

    def get_wallet_asset(
        self, user: User, user_wallet: Wallet, defi_provider: DefiProvider
    ):
        user_wallet_asset = ModelUtilityService.find_one(
            WalletAsset,
            {
                "wallet": user_wallet.id,
                "user": user.id,
                "blockchain": defi_provider.blockchain,
                "isDeleted": False,
            },
        )
        if user_wallet_asset is None:
            raise Exception("user asset not found")

        return user_wallet_asset

    def get_user_lending_data(
        self,
        user: User,
        defi_provider_id: PyObjectId = None,
    ):
        defi_provider = self.get_defi_provider(defi_provider_id)
        user_wallet = self.walletService.get_user_default_wallet(user)
        user_wallet_asset = self.get_wallet_asset(user, user_wallet, defi_provider)
        user_lending_data = self.lendingRegistry.get_service(
            defi_provider.serviceName
        ).get_user_account_data(
            eth_utils.to_bytes(hexstr=user_wallet_asset.address), defi_provider
        )

        return user_lending_data

    def get_reserved_assets(
        self,
        defi_provider_id: PyObjectId = None,
    ):
        defi_provider = self.get_defi_provider(defi_provider_id)
        reserved_assets = self.lendingRegistry.get_service(
            defi_provider.serviceName
        ).get_reserved_assets(defi_provider)

        return reserved_assets

    def get_user_config(
        self,
        user: User,
        defi_provider_id: PyObjectId = None,
    ):
        defi_provider = self.get_defi_provider(defi_provider_id)

        user_wallet = self.walletService.get_user_default_wallet(user)
        user_wallet_asset = self.get_wallet_asset(user, user_wallet, defi_provider)
        user_config_data = self.lendingRegistry.get_service(
            defi_provider.serviceName
        ).get_user_config(
            eth_utils.to_bytes(hexstr=user_wallet_asset.address), defi_provider
        )

        return user_config_data

    def borrow(
        self,
        user: User,
        payload: BorrowAssetDTO,
        defi_provider_id: PyObjectId = None,
    ):
        defi_provider = self.get_defi_provider(defi_provider_id)

        user_wallet = self.walletService.get_user_default_wallet(user)
        user_wallet_asset = self.get_wallet_asset(user, user_wallet, defi_provider)
        protocol_borrow_res = self.lendingRegistry.get_service(
            defi_provider.serviceName
        ).borrow(
            eth_utils.to_bytes(hexstr=payload.asset),
            payload.amount,
            payload.interestRateMode,
            eth_utils.to_bytes(hexstr=user_wallet_asset.address),
            defi_provider,
        )
        print("protocol_borrow_res", protocol_borrow_res)
        token_asset = BlockchainService.get_token_asset_by_query(
            {"contractAddress": payload.asset}
        )

        lending_req = ModelUtilityService.model_create(
            LendingRequest,
            LendingRequest(
                **{
                    "user": user.id,
                    "wallet": user_wallet.id,
                    "defiProvider": defi_provider.id,
                    "requestType": LendingRequestType.BORROW,
                    "status": LendingRequestStatus.OPEN,
                    "tokenAsset": (
                        token_asset.id if token_asset is not None else payload.asset
                    ),
                }
            ).dict(by_alias=True, exclude_none=True),
        )
        return lending_req

    def deposit(
        self,
        user: User,
        payload: DepositAssetDTO,
        defi_provider_id: PyObjectId = None,
    ):
        defi_provider = self.get_defi_provider(defi_provider_id)

        user_wallet = self.walletService.get_user_default_wallet(user)
        user_wallet_asset = self.get_wallet_asset(user, user_wallet, defi_provider)
        protocol_deposit_res = self.lendingRegistry.get_service(
            defi_provider.serviceName
        ).deposit(
            eth_utils.to_bytes(hexstr=payload.asset),
            payload.amount,
            eth_utils.to_bytes(hexstr=user_wallet_asset.address),
            defi_provider,
        )
        print("protocol_deposit_res", protocol_deposit_res)
        token_asset = BlockchainService.get_token_asset_by_query(
            {"contractAddress": payload.asset}
        )

        lending_req = ModelUtilityService.model_create(
            LendingRequest,
            LendingRequest(
                **{
                    "user": user.id,
                    "wallet": user_wallet.id,
                    "defiProvider": defi_provider.id,
                    "requestType": LendingRequestType.DEPOSIT,
                    "status": LendingRequestStatus.OPEN,
                    "tokenAsset": (
                        token_asset.id if token_asset is not None else payload.asset
                    ),
                }
            ).dict(by_alias=True, exclude_none=True),
        )
        return lending_req

    def repay(
        self,
        user: User,
        payload: BorrowAssetDTO,
        defi_provider_id: PyObjectId = None,
    ):
        defi_provider = self.get_defi_provider(defi_provider_id)

        user_wallet = self.walletService.get_user_default_wallet(user)
        user_wallet_asset = self.get_wallet_asset(user, user_wallet, defi_provider)
        protocol_repay_res = self.lendingRegistry.get_service(
            defi_provider.serviceName
        ).repay(
            eth_utils.to_bytes(hexstr=payload.asset),
            payload.amount,
            payload.interestRateMode,
            eth_utils.to_bytes(hexstr=user_wallet_asset.address),
            defi_provider,
        )
        print("protocol_repay_res", protocol_repay_res)
        token_asset = BlockchainService.get_token_asset_by_query(
            {"contractAddress": payload.asset}
        )

        lending_req = ModelUtilityService.model_create(
            LendingRequest,
            LendingRequest(
                **{
                    "user": user.id,
                    "wallet": user_wallet.id,
                    "defiProvider": defi_provider.id,
                    "requestType": LendingRequestType.DEPOSIT,
                    "status": LendingRequestStatus.OPEN,
                    "tokenAsset": (
                        token_asset.id if token_asset is not None else payload.asset
                    ),
                }
            ).dict(by_alias=True, exclude_none=True),
        )
        return lending_req
