from enum import Enum
from typing import Union

from bson import ObjectId
from pymongo import ASCENDING

from apps.user.interfaces.user_interface import UserOut
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
    user: Union[PyObjectId, UserOut]
    amount: int
    action: WalletAction
    previousBalance: int
    ref: str
    paymentMethod: PaymentMethod
    metaData: dict

    class Config:
        allow_population_by_alias = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    @staticmethod
    def init():
        db.wallettransaction.create_index([("ref", ASCENDING)], unique=True)
