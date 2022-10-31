from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from apps.appclient.services.appclient_service import AppClientService, Apps

from apps.marketdata.services.marketdata_iservice import IMarketDataService
from apps.marketdata.services.marketdata_type import IPriceData
from core.utils.request import REQUEST_METHOD, HTTPRepository
from core.utils.response_service import ResponseModel


class Roi(BaseModel):
    times: float
    currency: str
    percentage: float


class IGeckoPriceData(BaseModel):
    id: str
    symbol: str
    name: str
    image: str
    current_price: float
    market_cap: int
    market_cap_rank: int
    fully_diluted_valuation: Optional[int]
    total_volume: int
    high_24h: float
    low_24h: float
    price_change_24h: float
    price_change_percentage_24h: float
    market_cap_change_24h: int
    market_cap_change_percentage_24h: float
    circulating_supply: float
    total_supply: Optional[int]
    max_supply: Optional[int]
    ath: float
    ath_change_percentage: float
    ath_date: datetime
    atl: float
    atl_change_percentage: float
    atl_date: datetime
    roi: Optional[Roi]
    last_updated: datetime


class CoingeckoService(IMarketDataService):
    appClientService = AppClientService()

    def __init__(self) -> None:
        client_data = None

        try:
            client_data = self.appClientService.get_client_by_name(Apps.Coingecko)
        except Exception as e:
            print(e)

        self.base_url = client_data.appUrl if client_data else None
        self.httpRepository = HTTPRepository(
            self.base_url,
            {
                "X-CMC_PRO_API_KEY": client_data.clientSecret if client_data else None,
            },
        )

    def name(self) -> str:
        return "coingecko_service"

    async def get_historical_price_data(self) -> list[IPriceData]:
        price_data = await self.httpRepository.call(
            REQUEST_METHOD.GET,
            "/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100"
            "0&page=1&sparkline=false",
            ResponseModel[list[IGeckoPriceData]],
        )

        assert price_data.data, "coingecko market data is empty"

        return list(
            map(
                lambda data: IPriceData(
                    id=data.id,
                    name=data.name,
                    symbol=data.symbol,
                    price=data.current_price,
                    marketCap=data.market_cap,
                    circulatingSupply=data.circulating_supply,
                    totalSupply=data.total_supply,
                    maxSupply=data.max_supply,
                    priceChange24h=data.price_change_24h,
                    priceChangePercentage24h=data.price_change_percentage_24h,
                    marketCapChange24h=data.market_cap_change_24h,
                    marketCapChangePercentage24h=data.market_cap_change_percentage_24h,
                ),
                price_data.data,
            )
        )
