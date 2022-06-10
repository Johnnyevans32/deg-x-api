from typing import Any, Optional

from pydantic import BaseModel, Field


class EtherscanBaseResponse(BaseModel):
    status: str
    message: str
    result: Any


class IEtherscanNormalTxns(BaseModel):
    blockNumber: Optional[str]
    timeStamp: str
    hash: Optional[str]
    nonce: Optional[str]
    blockHash: Optional[str]
    transactionIndex: Optional[str]
    fromAddress: Optional[str] = Field(alias="from")
    to: Optional[str]
    value: Optional[str]
    gas: Optional[str]
    gasPrice: Optional[str]
    isError: Optional[str]
    txreceipt_status: Optional[str]
    input: Optional[str]
    contractAddress: Optional[str]
    cumulativeGasUsed: Optional[str]
    gasUsed: Optional[str]
    confirmations: Optional[str]
