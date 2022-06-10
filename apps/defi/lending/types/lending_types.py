from pydantic import BaseModel

from apps.defi.lending.interfaces.lending_interface import InterestRateMode


class BorrowAssetDTO(BaseModel):
    amount: float
    asset: str
    interestRateMode: InterestRateMode
