from datetime import datetime
from enum import Enum
from typing import Any, Union

from pydantic import Field
from pymongo import ASCENDING

from apps.blockchain.interfaces.network_interface import Network
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from core.db import db
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel, SBaseOutModel


class TxnType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"


class TxnSource(str, Enum):
    EXPLORER = "explorer"
    MANUAL = "manual"


class TxnStatus(str, Enum):
    PENDING = "pending"
    FAILED = "failed"
    SUCCESS = "success"


class BlockchainTransactionOut(SBaseOutModel):
    user: Union[PyObjectId, User]
    wallet: Union[PyObjectId, Wallet]
    network: Union[PyObjectId, Network]
    fromAddress: str
    toAddress: str
    transactionHash: str
    blockConfirmations: int
    blockNumber: int
    gasPrice: int
    gasUsed: int
    amount: float
    status: TxnStatus
    isContractExecution: bool
    txnType: TxnType
    source: TxnSource = Field(default=TxnSource.EXPLORER)
    transactedAt: datetime


class BlockchainTransaction(BlockchainTransactionOut, SBaseModel):
    metaData: Any

    @staticmethod
    def init() -> None:
        db.blockchaintransaction.create_index(
            [("transactionHash", ASCENDING)], unique=True
        )
