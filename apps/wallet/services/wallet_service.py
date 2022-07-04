from datetime import datetime

from mnemonic import Mnemonic
from pymongo.client_session import ClientSession

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.network_interface import NetworkType
from apps.blockchain.services.blockchain_service import BlockchainService
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet, WalletType
from apps.wallet.interfaces.walletasset_interface import WalletAsset

# from core.db import client
from core.db import db
from core.depends.get_object_id import PyObjectId
from core.utils.model_utility_service import ModelUtilityService


class WalletService:
    blockchainService = BlockchainService()
    mnemo = Mnemonic("english")

    async def update_wallet_balance(
        self, wallet_id, amount, session: ClientSession = None
    ) -> None:
        db.wallet.update_one(
            {"_id": wallet_id},
            {"$inc": {"balance": amount}, "$set": {"updatedAt": datetime.now()}},
            session=session,
        )

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
    ) -> Wallet:
        try:
            # if not session:
            #     session = client.start_session()
            #     session.start_transaction()
            mnemonic = self.mnemo.generate(strength=256)
            dict_wallet = Wallet(
                **{
                    "user": user.id,
                    "name": "multi-coin wallet",
                    "walletType": walletType,
                    "mnemonic": mnemonic,
                }
            ).dict(by_alias=True, exclude_none=True)

            await ModelUtilityService.model_find_one_and_update(
                Wallet,
                {"user": user.id, "isDeleted": False, "isDefault": True},
                {"isDefault": False},
            )

            wallet_obj = await ModelUtilityService.model_create(
                Wallet, dict_wallet, session
            )
            blockchains = await BlockchainService.get_blockchains(
                {"isDeleted": {"$ne": True}}
            )

            for chain in blockchains:
                await self.create_wallet_assets(
                    user, wallet_obj, session, mnemonic, chain
                )

            return wallet_obj
        except Exception as e:
            raise e

    async def create_wallet_assets(
        self,
        user: User,
        wallet: Wallet,
        session: ClientSession,
        mnemonic: str,
        chain: Blockchain,
    ) -> None:
        address = self.blockchainService.create_address(chain.registryName, mnemonic)

        token_assets = await BlockchainService.get_token_assets(
            {"isDeleted": False, "blockchain": chain.id, "isLayerOne": True}
        )
        dict_wallet_assets = list(
            map(
                lambda token_asset: WalletAsset(
                    **{
                        "user": user.id,
                        "wallet": wallet.id,
                        "tokenasset": token_asset.id,
                        "address": address,
                        "blockchain": chain.id,
                    }
                ).dict(by_alias=True, exclude_none=True),
                token_assets,
            )
        )

        await ModelUtilityService.model_create_many(
            WalletAsset, dict_wallet_assets, session
        )

    async def retrieve_wallet_assets(self, user: User) -> list[WalletAsset]:
        user_wallet = await self.get_user_default_wallet(user)
        res = await ModelUtilityService.find_and_populate(
            WalletAsset, {"wallet": user_wallet.id, "isDeleted": False}, ["tokenasset"]
        )
        return res

    async def retrieve_user_wallets(self, user: User) -> list[Wallet]:
        user_wallets = await ModelUtilityService.find(
            Wallet, {"user": user.id, "isDeleted": False}
        )
        if not user_wallets:
            raise Exception("wallets not found")
        return user_wallets

    async def update_wallet_network(self, user: User, network_type: NetworkType):
        user_def_wallet = await ModelUtilityService.model_update(
            Wallet,
            {"user": user.id, "isDeleted": False, "isDefault": True},
            {"networkType": network_type},
        )

        print("user_def_wallet", user_def_wallet.raw_result)

    async def update_dafault_wallet(self, user: User, wallet_id: PyObjectId):
        await ModelUtilityService.model_find_one_and_update(
            Wallet,
            {"user": user.id, "isDeleted": False, "isDefault": True},
            {"isDefault": False},
        )

        user_def_wallet = await ModelUtilityService.model_update(
            Wallet,
            {"_id": wallet_id, "user": user.id, "isDeleted": False},
            {"isDefault": True},
        )

        print("user_def_wallet", user_def_wallet)

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
