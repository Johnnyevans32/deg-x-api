from enum import Enum
from typing import Any, Union


from apps.blockchain.interfaces.network_interface import Network
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet

from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel, SBaseOutModel


class TxnStatus(str, Enum):
    PENDING = "pending"
    FAILED = "failed"
    SUCCESS = "success"


class TestTokenOut(SBaseOutModel):
    user: Union[PyObjectId, User]
    wallet: Union[PyObjectId, Wallet]
    network: Union[PyObjectId, Network]
    transactionHash: str
    amount: float
    status: TxnStatus


class TestToken(TestTokenOut, SBaseModel):
    metaData: Any
