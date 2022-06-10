from enum import Enum
from typing import Union

from pymongo import ASCENDING
from apps.blockchain.interfaces.transaction_interface import TxnType

from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from core.db import db
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel


class PaymentMethod(str, Enum):
    INTERNAL = "internalFund"


class WalletTransaction(SBaseModel):
    wallet: Union[PyObjectId, Wallet]
    user: Union[PyObjectId, User]
    amount: int
    action: TxnType
    previousBalance: int
    ref: str
    paymentMethod: PaymentMethod
    metaData: dict

    @staticmethod
    def init():
        db.wallettransaction.create_index([("ref", ASCENDING)], unique=True)
