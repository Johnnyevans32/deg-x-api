from pydantic import BaseModel

from apps.defi.lending.interfaces.lending_request_interface import InterestRateMode


class BaseLendingActionDTO(BaseModel):
    amount: float
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
