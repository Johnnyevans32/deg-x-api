from typing import Any, cast

from mnemonic import Mnemonic
from pymongo.client_session import ClientSession

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.network_interface import NetworkType
from apps.blockchain.services.blockchain_service import BlockchainService
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet, WalletType
from apps.wallet.interfaces.walletasset_interface import WalletAsset

# from core.db import client
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

    async def create_wallet(
        self,
        user: User,
        session: ClientSession = None,
        walletType: WalletType = WalletType.MULTICHAIN,
    ) -> tuple[Wallet, EncryptedDTO]:
        assert user.id, "user id not found"
        mnemonic = self.mnemo.generate(strength=256)
        dict_wallet = Wallet(
            user=user.id,
            name="multi-coin wallet",
            walletType=walletType,
        ).dict(by_alias=True, exclude_none=True)

        await ModelUtilityService.model_find_one_and_update(
            Wallet,
            {"user": user.id, "isDeleted": False, "isDefault": True},
            {"isDefault": False},
        )

        encrypted_mnemonic_obj = self.aesEncryptionService.encrypt_AES_GCM(mnemonic)
        wallet_obj = await ModelUtilityService.model_create(
            Wallet, dict_wallet, session
        )
        qr_code_image = await Utils.create_qr_image(user.username)

        wallet_obj = (
            await ModelUtilityService.model_find_one_and_update(
                Wallet,
                {"_id": wallet_obj.id},
                {"qrImage": qr_code_image},
                session=session,
            )
            or wallet_obj
        )
        blockchains = await BlockchainService.get_blockchains(
            {"isDeleted": {"$ne": True}}
        )

        for chain in blockchains:
            await self.create_wallet_assets(user, wallet_obj, mnemonic, chain, session)

        return wallet_obj, encrypted_mnemonic_obj

    async def create_wallet_assets(
        self,
        user: User,
        wallet: Wallet,
        mnemonic: str,
        chain: Blockchain,
        session: ClientSession = None,
    ) -> None:
        address = await self.blockchainService.create_address(
            chain.registryName, mnemonic
        )

        token_assets = await BlockchainService.get_token_assets(
            {"isDeleted": False, "blockchain": chain.id, "isLayerOne": True}
        )
        dict_wallet_assets = list(
            map(
                lambda token_asset: WalletAsset(
                    user=cast(PyObjectId, user.id),
                    wallet=cast(PyObjectId, wallet.id),
                    tokenasset=cast(PyObjectId, token_asset.id),
                    address=address,
                    blockchain=cast(PyObjectId, chain.id),
                ).dict(by_alias=True, exclude_none=True),
                token_assets,
            )
        )

        await ModelUtilityService.model_create_many(
            WalletAsset, dict_wallet_assets, session
        )

    async def retrieve_wallet_assets(self, user: User) -> list[WalletAsset]:
        user_wallet = await self.get_user_default_wallet(user)
        user_assets = await ModelUtilityService.find_and_populate(
            WalletAsset, {"wallet": user_wallet.id, "isDeleted": False}, ["tokenasset"]
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

    # def debit_wallet(
    #     self, user: User, amount: int, ref: str, session: ClientSession = None
    # ) -> None:
    #     mutex = threading.Lock()

    #     mutex.acquire()
    #     try:
    #         user_wallet = self.get_user_wallet(user.id)

    #         if user_wallet.balance < amount:
    #             raise Exception("wallet balance insufficient")

    #         wallet_transaction_data = {
    #             "wallet": user_wallet.id,
    #             "user": user.id,
    #             "action": WalletAction.debit.value,
    #             "amount": amount,
    #             "previousBalance": user_wallet.balance,
    #             "ref": ref,
    #         }
    #         self.update_wallet_balance(user_wallet.id, -amount, session)
    #         ModelUtilityService.model_create(
    #             WalletTransaction,
    #             wallet_transaction_data,
    #             session,
    #         )
    #     except Exception as e:
    #         raise e
    #     finally:
    #         mutex.release()

    # def credit_wallet(
    #     self, user: User, amount: int, ref: str, paymentMethod: str, metaData: Any
    # ) -> None:
    #     mutex = threading.Lock()

    #     mutex.acquire()

    #     session = client.start_session()
    #     session.start_transaction()
    #     try:
    #         user_wallet = self.get_user_wallet(user.id)
    #         wallet_transaction_data = {
    #             "wallet": user_wallet.id,
    #             "user": user.id,
    #             "action": WalletAction.credit.value,
    #             "amount": amount,
    #             "previousBalance": user_wallet.balance,
    #             "ref": ref,
    #             "metaData": metaData,
    #             "paymentMethod": paymentMethod,
    #         }
    #         self.update_wallet_balance(user_wallet.id, amount, session)
    #         ModelUtilityService.model_create(
    #             WalletTransaction,
    #             wallet_transaction_data,
    #             session,
    #         )
    #         session.commit_transaction()
    #     except Exception as e:
    #         # operation exception, interrupt transaction
    #         session.abort_transaction()
    #         raise e
    #     finally:
    #         session.end_session()
    #         mutex.release()
