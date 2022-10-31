from typing import Optional
from pydantic import BaseModel


class IPriceData(BaseModel):
    id: str
    name: str
    symbol: str
    price: float
    marketCap: float
    circulatingSupply: float
    totalSupply: Optional[int]
    maxSupply: Optional[int]
    priceChange24h: float
    priceChangePercentage24h: float
    marketCapChange24h: Optional[int]
    marketCapChangePercentage24h: Optional[float]
