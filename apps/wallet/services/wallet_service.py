from datetime import datetime
from functools import partial

from mnemonic import Mnemonic
from pymongo.client_session import ClientSession

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.services.blockchain_service import BlockchainService
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet, WalletType
from apps.wallet.interfaces.walletasset_interface import WalletAsset
from core.db import db
from core.utils.model_utility_service import ModelUtilityService


class WalletService:
    blockchainService = BlockchainService()
    mnemo = Mnemonic("english")

    def update_wallet_balance(
        self, wallet_id, amount, session: ClientSession = None
    ) -> None:
        db.wallet.update_one(
            {"_id": wallet_id},
            {"$inc": {"balance": amount}, "$set": {"updatedAt": datetime.now()}},
            session=session,
        )

    def get_user_default_wallet(self, user: User) -> Wallet:
        user_default_wallet = ModelUtilityService.find_one(
            Wallet, {"user": user.id, "isDeleted": False, "isDefault": True}
        )

        if user_default_wallet is None:
            raise Exception("default wallet not set")
        return user_default_wallet

    def create_wallet(
        self,
        user: User,
        session: ClientSession,
        walletType: WalletType = WalletType.MULTICHAIN,
    ) -> None:
        try:
            mnemonic = self.mnemo.generate(strength=256)
            dict_wallet = Wallet(
                **{
                    "user": user.id,
                    "name": "multi-coin wallet",
                    "walletType": walletType,
                    "mnemonic": mnemonic,
                }
            ).dict(by_alias=True, exclude_none=True)

            wallet_obj = ModelUtilityService.model_create(Wallet, dict_wallet, session)
            blockchains = BlockchainService.get_blockchains(
                {"isDeleted": {"$ne": True}}
            )
            list(
                map(
                    partial(
                        self.create_wallet_assets, user, wallet_obj, session, mnemonic
                    ),
                    blockchains,
                )
            )

        except Exception as e:
            raise e

    def create_wallet_assets(
        self,
        user: User,
        wallet: Wallet,
        session: ClientSession,
        mnemonic: str,
        chain: Blockchain,
    ) -> None:
        address = self.blockchainService.create_address(chain.registryName, mnemonic)

        token_assets = BlockchainService.get_token_assets(
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

        ModelUtilityService.model_create_many(WalletAsset, dict_wallet_assets, session)

    def retrieve_wallet_assets(self, user: User) -> list[WalletAsset]:
        user_wallet = self.retrieve_default_wallet(user)
        res = ModelUtilityService.find_and_populate(
            WalletAsset, {"wallet": user_wallet.id, "isDeleted": False}, ["tokenasset"]
        )
        return res

    def retrieve_default_wallet(self, user: User) -> Wallet:
        db_resp = db.wallet.find_one({"user": user.id, "isDeleted": False})
        if db_resp is None:
            raise Exception("user wallet not found")
        return Wallet(**db_resp)

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
