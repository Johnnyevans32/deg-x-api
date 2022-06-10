import eth_utils

from apps.blockchain.services.blockchain_service import BlockchainService
from apps.defi.interfaces.defi_provider_interface import DefiProvider, DefiServiceType
from apps.defi.lending.interfaces.lending_request_interface import (
    LendingRequest,
    LendingRequestStatus,
    LendingRequestType,
)
from apps.defi.lending.services.lending_registry import LendingRegistry
from apps.defi.lending.types.lending_types import BorrowAssetDTO
from apps.user.interfaces.user_interface import User
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
        defualt_lending_provider = ModelUtilityService.find_one_and_populate(
            DefiProvider,
            {
                "isDefault": True,
                "serviceType": DefiServiceType.LENDING,
                "isDeleted": False,
            },
            ["network"],
            True,
        )

        return defualt_lending_provider

    def get_user_lending_data(
        self,
        user: User,
        defi_provider_id: PyObjectId = None,
    ):

        if defi_provider_id is None:
            defi_provider = LendingService.get_default_provider_key()
        else:
            defi_provider = ModelUtilityService.find_one_and_populate(
                DefiProvider, {"_id": defi_provider_id}, ["network"], True
            )

        user_wallet = self.walletService.get_user_default_wallet(user)
        user_wallet_asset = ModelUtilityService.find_one(
            WalletAsset,
            {
                "wallet": user_wallet.id,
                "user": user.id,
                "blockchain": defi_provider.blockchain,
                "isDeleted": False,
            },
            True,
        )
        user_lending_data = self.lendingRegistry.get_service(
            defi_provider.serviceName
        ).get_user_account_data(
            eth_utils.to_bytes(hexstr=user_wallet_asset.address), defi_provider
        )

        return user_lending_data

    def get_user_config(
        self,
        user: User,
        defi_provider_id: PyObjectId = None,
    ):
        if defi_provider_id is None:
            defi_provider = LendingService.get_default_provider_key()
        else:
            defi_provider = ModelUtilityService.find_one_and_populate(
                DefiProvider, {"_id": defi_provider_id}, ["network"], True
            )

        user_wallet = self.walletService.get_user_default_wallet(user)
        user_wallet_asset = ModelUtilityService.find_one(
            WalletAsset,
            {
                "wallet": user_wallet.id,
                "user": user.id,
                "blockchain": defi_provider.blockchain,
                "isDeleted": False,
            },
            True,
        )
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
        if defi_provider_id is None:
            defi_provider = LendingService.get_default_provider_key()
        else:
            defi_provider = ModelUtilityService.find_one_and_populate(
                DefiProvider, {"_id": defi_provider_id}, ["network"], True
            )

        user_wallet = self.walletService.get_user_default_wallet(user)
        user_wallet_asset = ModelUtilityService.find_one(
            WalletAsset,
            {
                "wallet": user_wallet.id,
                "user": user.id,
                "blockchain": defi_provider.blockchain,
                "isDeleted": False,
            },
            True,
        )
        protocol_borrow_res = self.lendingRegistry.get_service(
            defi_provider.serviceName
        ).borrow(
            eth_utils.to_bytes(hexstr=payload.asset),
            payload.amount,
            payload.interestRateMode,
            eth_utils.to_bytes(hexstr=user_wallet_asset.address),
            defi_provider,
        )

        token_asset = BlockchainService.get_token_asset_by_query(
            {"contractAddress": payload.asset}
        )

        ModelUtilityService.model_create(
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
        return protocol_borrow_res
