from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class IGasSpeed(BaseModel):
    acceptance: float
    maxFeePerGas: Optional[float] = None
    maxPriorityFeePerGas: Optional[float] = None
    baseFee: Optional[float] = None
    gasPrice: Optional[float] = None
    estimatedFee: float


class IOwlRacleFeeInfo(BaseModel):
    timestamp: datetime
    lastBlock: int
    avgTime: float
    avgTx: float
    avgGas: float
    speeds: list[IGasSpeed]
