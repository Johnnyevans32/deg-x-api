from pydantic import BaseModel

from apps.defi.lending.interfaces.lending_request_interface import InterestRateMode


class BorrowAssetDTO(BaseModel):
    amount: float
    asset: str
    interestRateMode: InterestRateMode


class DepositAssetDTO(BaseModel):
    amount: float
    asset: str
    interestRateMode: InterestRateMode
