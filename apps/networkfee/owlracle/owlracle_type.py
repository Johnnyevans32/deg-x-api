from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class IGasSpeed(BaseModel):
    acceptance: float
    maxFeePerGas: Optional[float]
    maxPriorityFeePerGas: Optional[float]
    baseFee: Optional[float]
    gasPrice: Optional[float]
    estimatedFee: float


class IOwlRacleFeeInfo(BaseModel):
    timestamp: datetime
    lastBlock: int
    avgTime: float
    avgTx: float
    avgGas: float
    speeds: list[IGasSpeed]
