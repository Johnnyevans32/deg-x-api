import asyncio
from typing import Any, cast

from mnemonic import Mnemonic
from pymongo.client_session import ClientSession

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.network_interface import Network, NetworkType
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset, TokenAssetCore
from apps.blockchain.services.blockchain_service import BlockchainService
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet, WalletType
from apps.wallet.interfaces.walletasset_interface import WalletAsset

from core.db import client
from core.depends.get_object_id import PyObjectId
from core.utils.aes import AesEncryptionService, EncryptedDTO
from core.utils.model_utility_service import ModelUtilityService
from core.utils.utils_service import Utils


class WalletService:
    mnemo = Mnemonic("english")
    blockchainService = BlockchainService()
    aesEncryptionService = AesEncryptionService()

    async def get_wallet_by_query(self, query: dict[str, Any]) -> Wallet:
        wallet = await ModelUtilityService.find_one(Wallet, query)
        if wallet is None:
            raise Exception("wallet not found")
        return wallet

    async def get_walletasset_by_query(self, query: dict[str, Any]) -> WalletAsset:
        wallet_asset = await ModelUtilityService.find_one(WalletAsset, query)
        if wallet_asset is None:
            raise Exception("wallet not found")
        return wallet_asset

    async def get_user_default_wallet(self, user: User) -> Wallet:
        user_default_wallet = await ModelUtilityService.find_one(
            Wallet, {"user": user.id, "isDeleted": False, "isDefault": True}
        )

        if user_default_wallet is None:
            raise Exception("default wallet not set")
        return user_default_wallet

    async def get_user_default_wallet_without_error(self, user: User) -> Wallet | None:
        user_default_wallet = await ModelUtilityService.find_one(
            Wallet, {"user": user.id, "isDeleted": False, "isDefault": True}
        )
        return user_default_wallet

    async def create_wallet_with_session(
        self,
        user: User,
    ) -> tuple[Wallet, EncryptedDTO]:
        session = client.start_session()
        session.start_transaction()
        try:
            res = await self.create_wallet(user, session)
            print("done")
            session.commit_transaction()
            print("commit_transaction done")
            return res
        except Exception as e:
            print(e)
            session.abort_transaction()
            raise e
        finally:
            session.end_session()

    async def create_wallet(
        self,
        user: User,
        session: ClientSession | None = None,
        walletType: WalletType = WalletType.MULTICHAIN,
    ) -> tuple[Wallet, EncryptedDTO]:
        assert user.id, "user id not found"

        mnemonic = self.mnemo.generate(strength=256)
        dict_wallet = Wallet(
            user=user.id,
            name="multi-coin wallet",
            walletType=walletType,
        ).dict(by_alias=True, exclude_none=True)

        encrypted_mnemonic_obj = await self.aesEncryptionService.encrypt_AES_GCM(
            mnemonic
        )
        wallet_obj = await ModelUtilityService.model_create(
            Wallet, dict_wallet, session
        )

        blockchains = await BlockchainService.get_blockchains(
            {"isDeleted": {"$ne": True}}
        )

        await Utils.promise_all(
            [
                self.create_wallet_assets(user, wallet_obj, mnemonic, chain, session)
                for chain in blockchains
            ]
        )

        await ModelUtilityService.model_find_one_and_update(
            Wallet,
            {
                "user": user.id,
                "isDeleted": False,
                "_id": {"$ne": wallet_obj.id},
                "isDefault": True,
            },
            {"isDefault": False},
        )

        return wallet_obj, encrypted_mnemonic_obj

    async def create_wallet_assets(
        self,
        user: User,
        wallet: Wallet,
        mnemonic: str,
        chain: Blockchain,
        session: ClientSession | None = None,
    ) -> None:

        address = await self.blockchainService.create_address(
            chain.registryName, mnemonic
        )

        token_assets = await BlockchainService.get_token_assets(
            {"isDeleted": False, "blockchain": chain.id, "isLayerOne": True}
        )
        loop = asyncio.get_event_loop()

        def convert_assets_to_dict() -> list[dict[str, Any]]:
            return list(
                map(
                    lambda token_asset: WalletAsset(
                        user=cast(PyObjectId, user.id),
                        wallet=cast(PyObjectId, wallet.id),
                        tokenasset=cast(PyObjectId, token_asset.id),
                        address=self.blockchainService.get_address(
                            address, cast(Network, token_asset.network)
                        ),
                        qrImage=Utils.create_qr_image(
                            self.blockchainService.get_address(
                                address, cast(Network, token_asset.network)
                            )
                        ),
                        networkType=cast(Network, token_asset.network).networkType,
                        blockchain=cast(PyObjectId, chain.id),
                    ).dict(by_alias=True, exclude_none=True),
                    token_assets,
                )
            )

        print("brpooing for ", chain.name)
        dict_wallet_assets = await loop.run_in_executor(None, convert_assets_to_dict)

        print("creating for ", chain.name)
        await ModelUtilityService.model_create_many(
            WalletAsset, dict_wallet_assets, session
        )

    async def retrieve_wallet_assets(self, user: User) -> list[WalletAsset]:
        user_wallet = await self.get_user_default_wallet(user)
        user_assets = await ModelUtilityService.find_and_populate(
            WalletAsset,
            {
                "wallet": user_wallet.id,
                "networkType": user_wallet.networkType,
                "isDeleted": False,
            },
            ["tokenasset", "blockchain", "tokenasset.network"],
        )
        return user_assets

    async def retrieve_user_wallets(self, user: User) -> list[Wallet]:
        user_wallets = await ModelUtilityService.find(
            Wallet, {"user": user.id, "isDeleted": False}
        )
        if not user_wallets:
            raise Exception("wallets not found")
        return user_wallets

    async def update_wallet_network(
        self, user: User, network_type: NetworkType
    ) -> None:
        await ModelUtilityService.model_update(
            Wallet,
            {"user": user.id, "isDeleted": False, "isDefault": True},
            {"networkType": network_type},
        )

    async def update_dafault_wallet(self, user: User, wallet_id: PyObjectId) -> None:
        await ModelUtilityService.model_find_one_and_update(
            Wallet,
            {"user": user.id, "isDeleted": False, "isDefault": True},
            {"isDefault": False},
        )

        await ModelUtilityService.model_update(
            Wallet,
            {"_id": wallet_id, "user": user.id, "isDeleted": False},
            {"isDefault": True},
        )

    async def add_token_asset(self, user: User, payload: TokenAssetCore) -> WalletAsset:
        network = await self.blockchainService.get_network_by_query(
            {
                "_id": payload.network,
            }
        )
        user_wallet = await self.get_user_default_wallet(user)
        token_asset = await ModelUtilityService.model_find_one_or_create(
            TokenAsset,
            {
                "contractAddress": payload.contractAddress,
                "network": payload.network,
                "isDeleted": False,
            },
            {"name": "", "symbol": "", "blockchain": network.blockchain},
        )
        default_wallet_asset_query = {
            "user": user.id,
            "networkType": network.networkType,
            "wallet": user_wallet.id,
            "isDeleted": False,
        }
        wallet_asset_w_address = await ModelUtilityService.find_one(
            WalletAsset,
            {
                **default_wallet_asset_query,
                "blockchain": network.blockchain,
            },
        )
        assert wallet_asset_w_address, "asset address not found"
        wallet_asset = await ModelUtilityService.model_find_one_or_create(
            WalletAsset,
            {
                **default_wallet_asset_query,
                "tokenasset": token_asset.id,
            },
            {
                "blockchain": network.blockchain,
                "address": wallet_asset_w_address.address,
            },
        )

        return wallet_asset
