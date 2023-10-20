from pydantic import BaseModel


class IPriceData(BaseModel):
    id: str
    name: str
    symbol: str
    price: float
    marketCap: float
    circulatingSupply: float
    totalSupply: float | None = None
    maxSupply: float | None = None
    priceChange24h: float | None
    priceChangePercentage24h: float | None
    marketCapChange24h: float | None = None
    marketCapChangePercentage24h: float | None = None
