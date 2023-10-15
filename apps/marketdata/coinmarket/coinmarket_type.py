from pydantic import BaseModel
from datetime import datetime
from typing import Generic, TypeVar


class RequestStatus(BaseModel):
    timestamp: datetime
    error_code: int
    error_message: str
    elapsed: int
    credit_count: int


class CurrencyQuote(BaseModel):
    price: float
    volume_24h: int
    percent_change_1h: float
    percent_change_24h: float
    percent_change_7d: float
    market_cap: int
    last_updated: datetime


class IHistoricalPriceData(BaseModel):
    id: int
    name: str
    symbol: str
    slug: str
    cmc_rank: int
    num_market_pairs: int
    circulating_supply: int
    total_supply: int
    max_supply: int
    last_updated: datetime
    date_added: datetime
    tags: list[str]
    platform: str
    quote: dict[str, CurrencyQuote]


T = TypeVar("T")


class BaseResponseModel(BaseModel, Generic[T]):
    status: RequestStatus
    data: T
