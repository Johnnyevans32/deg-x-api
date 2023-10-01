from pydantic import BaseModel


class IPriceData(BaseModel):
    id: str
    name: str
    symbol: str
    price: float
    marketCap: float
    circulatingSupply: float
    totalSupply: int | None = None
    maxSupply: int | None = None
    priceChange24h: float | None
    priceChangePercentage24h: float | None
    marketCapChange24h: int | None = None
    marketCapChangePercentage24h: float | None = None
