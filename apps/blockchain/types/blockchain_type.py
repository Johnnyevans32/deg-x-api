from enum import Enum
from pydantic import BaseModel


class ReceipientType(str, Enum):
    USERNAME = "username"
    WALLET = "wallet"
    ADDRESS = "address"


class GetTokenBalance(BaseModel):
    asset: str


class BaseTxnSendDTO(BaseModel):
    amount: float


class GetTestTokenDTO(GetTokenBalance, BaseTxnSendDTO):
    pass


class SwapTokenDTO(GetTokenBalance, BaseTxnSendDTO):
    mnemonic: str


class SendTokenDTO(SwapTokenDTO):
    receipient: str
    receipientType: ReceipientType = ReceipientType.ADDRESS


class SendTxnRes(BaseModel):
    transactionHash: str


class BalanceRes(BaseModel):
    symbol: str
    balance: float
