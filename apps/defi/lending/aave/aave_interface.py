from pydantic import BaseModel


class IUserAcccountData(BaseModel):
    totalCollateralETH: float
    totalDebtETH: float
    availableBorrowsETH: float
    currentLiquidationThreshold: float
    ltv: float
    healthFactory: float


class IReserveTokens(BaseModel):
    tokenSymbol: str
    tokenAddress: str
