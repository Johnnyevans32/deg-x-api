from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class EtherscanBaseResponse(BaseModel, Generic[T]):
    status: str
    message: str
    result: T


class IEtherscanNormalTxns(BaseModel):
    blockNumber: Optional[int] = None
    timeStamp: str
    hash: str
    nonce: Optional[str] = None
    blockHash: Optional[str] = None
    transactionIndex: Optional[str] = None
    fromAddress: Optional[str] = Field(alias="from", default=None)
    to: Optional[str] = None
    value: Optional[str] = None
    gas: Optional[str] = None
    gasPrice: Optional[int] = None
    isError: Optional[str] = None
    txreceipt_status: Optional[str] = None
    input: Optional[str] = None
    contractAddress: Optional[str] = None
    cumulativeGasUsed: Optional[str] = None
    gasUsed: Optional[int] = None
    confirmations: Optional[str] = None
