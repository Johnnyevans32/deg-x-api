from typing import Any, Optional
from pydantic import BaseModel

from apps.defi.lending.interfaces.lending_request_interface import InterestRateMode
from core.depends.get_object_id import PyObjectId


class BaseLendingActionDTO(BaseModel):
    amount: float
    provider: Optional[PyObjectId]
    asset: str
    mnemonic: str

    class Config:
        schema_extra = {
            "example": {
                "asset": "0xd0A1E359811322d97991E03f863a0C30C2cF029C",
                "amount": 0.02,
            }
        }


class BorrowAssetDTO(BaseLendingActionDTO):
    interestRateMode: InterestRateMode


class IUserAcccountData(BaseModel):
    totalCollateral: float
    totalDebt: float
    availableBorrows: float
    currentLiquidationThreshold: Optional[float]
    ltv: Optional[float]
    healthFactory: float


class IReserveToken(BaseModel):
    tokenSymbol: str
    tokenAddress: str
    usageAsCollateralEnabled: bool
    borrowingEnabled: bool
    liquidityRate: Any
    availableLiquidity: Any
    variableBorrowRate: Any
    stableBorrowRate: Any
    ltv: Any
