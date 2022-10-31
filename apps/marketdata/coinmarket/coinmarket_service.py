from apps.appclient.services.appclient_service import AppClientService, Apps
from apps.marketdata.coinmarket.coinmarket_type import (
    BaseResponseModel,
    IHistoricalPriceData,
)

from apps.marketdata.services.marketdata_iservice import IMarketDataService
from apps.marketdata.services.marketdata_type import IPriceData
from core.utils.request import REQUEST_METHOD, HTTPRepository


class CoinmarketService(IMarketDataService):
    appClientService = AppClientService()

    def __init__(self) -> None:
        client_data = None

        try:
            client_data = self.appClientService.get_client_by_name(Apps.Coinmarket)
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
        return "coinmarket_service"

    async def get_historical_price_data(self) -> list[IPriceData]:
        price_data = await self.httpRepository.call(
            REQUEST_METHOD.GET,
            "/v1/cryptocurrency/listings/historical",
            BaseResponseModel[list[IHistoricalPriceData]],
        )

        def reform_data(data: IHistoricalPriceData) -> IPriceData:
            id = str(data.id)
            price = data.quote["USD"].price
            priceChangePercentage24h = data.quote["USD"].percent_change_24h
            return IPriceData(
                id=id,
                name=data.name,
                symbol=data.symbol,
                price=price,
                marketCap=data.quote["USD"].market_cap,
                circulatingSupply=data.circulating_supply,
                totalSupply=data.total_supply,
                maxSupply=data.max_supply,
                priceChange24h=(priceChangePercentage24h / 100) * price,
                priceChangePercentage24h=priceChangePercentage24h,
            )

        return list(map(reform_data, price_data.data))
