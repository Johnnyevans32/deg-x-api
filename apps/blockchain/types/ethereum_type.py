from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar("T")


class EtherscanBaseResponse(GenericModel, Generic[T]):
    status: str
    message: str
    result: T


class IEtherscanNormalTxns(BaseModel):
    blockNumber: Optional[int]
    timeStamp: str
    hash: str
    nonce: Optional[str]
    blockHash: Optional[str]
    transactionIndex: Optional[str]
    fromAddress: Optional[str] = Field(alias="from")
    to: Optional[str]
    value: Optional[str]
    gas: Optional[str]
    gasPrice: Optional[int]
    isError: Optional[str]
    txreceipt_status: Optional[str]
    input: Optional[str]
    contractAddress: Optional[str]
    cumulativeGasUsed: Optional[str]
    gasUsed: Optional[int]
    confirmations: Optional[str]
