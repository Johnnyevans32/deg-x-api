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
from core.depends import PyObjectId
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

    def create_wallet(
        self,
        user: User,
        session: ClientSession,
        walletType: WalletType = WalletType.multichain,
    ) -> None:
        try:
            mnemonic = self.mnemo.generate(strength=256)
            dict_wallet = {
                "user": user.id,
                "name": "dummy",
                "walletType": walletType,
                "mnemonic": mnemonic,
            }

            wallet_obj = ModelUtilityService.model_create(Wallet, dict_wallet, session)
            blockchains = BlockchainService.get_blockchains()
            list(
                map(
                    partial(
                        self.create_wallet_assets, user, wallet_obj, session, mnemonic
                    ),
                    blockchains,
                )
            )

        except Exception as e:
            print(e)
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
            {"isDeleted": False, "isLayerOne": True}
        )
        dict_wallet_assets = list(
            map(
                lambda token_asset: {
                    "user": user.id,
                    "wallet": wallet.id,
                    "tokenasset": token_asset.id,
                    "address": address,
                },
                token_assets,
            )
        )

        ModelUtilityService.model_create_many(WalletAsset, dict_wallet_assets, session)

    def retrieve_wallet_assets(self, user: User) -> list[WalletAsset]:
        user_wallet = self.retrieve_wallet(user)
        res = ModelUtilityService.find_and_populate(
            WalletAsset, {"wallet": user_wallet.id, "isDeleted": False}, ["tokenasset"]
        )
        print(res)
        return res

    def retrieve_wallet(self, user: User) -> Wallet:
        db_resp = db.wallet.find_one({"user": user.id, "isDeleted": False})
        if db_resp is None:
            raise Exception("user wallet not found")
        return Wallet(**db_resp)

    def get_user_wallet(self, user_id: PyObjectId) -> Wallet:
        db_resp = db.wallet.find_one({"user": user_id, "isDeleted": False})
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
