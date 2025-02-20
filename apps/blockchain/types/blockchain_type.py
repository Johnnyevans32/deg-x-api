from enum import Enum
from pydantic import BaseModel, ConfigDict
from core.depends.get_object_id import PyObjectId


class ReceipientType(str, Enum):
    USERNAME = "username"
    ADDRESS = "address"


class GetTokenBalance(BaseModel):
    walletasset: PyObjectId


class BaseTxnSendDTO(BaseModel):
    amount: float


class GetTestTokenDTO(BaseTxnSendDTO):
    asset: str


class SwapTokenDTO(GetTokenBalance, BaseTxnSendDTO):
    mnemonic: str


class SendTokenDTO(SwapTokenDTO):
    receipient: str
    receipientType: ReceipientType = ReceipientType.ADDRESS

    model_config = ConfigDict(str_strip_whitespace=True, str_to_lower=True)


class SendTxnRes(BaseModel):
    transactionHash: str


class BalanceRes(BaseModel):
    symbol: str
    balance: float
