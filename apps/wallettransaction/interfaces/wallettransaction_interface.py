from enum import Enum
from typing import Union


from pymongo import ASCENDING

from apps.user.interfaces.user_interface import User
from core.db import db
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel


class PaymentMethod(str, Enum):
    internalFund = "internalFund"


class WalletAction(str, Enum):
    credit = "credit"
    debit = "debit"


class WalletTransaction(SBaseModel):
    wallet: PyObjectId
    user: Union[PyObjectId, User]
    amount: int
    action: WalletAction
    previousBalance: int
    ref: str
    paymentMethod: PaymentMethod
    metaData: dict

    @staticmethod
    def init():
        db.wallettransaction.create_index([("ref", ASCENDING)], unique=True)
