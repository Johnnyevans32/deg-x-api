from apps.marketdata.registry.marketdata_registry import MarketDataRegistry
from apps.marketdata.services.marketdata_type import IPriceData
from core.utils.utils_service import timed_cache


class MarketDataService:
    marketDataRegistry = MarketDataRegistry()

    def get_default_marketdata_provider(self) -> str:
        return "coingecko_service"

    @timed_cache(10, 1, asyncFunction=True)
    async def get_historical_price_data(self) -> list[IPriceData]:
        price_data = await self.marketDataRegistry.get_service(
            self.get_default_marketdata_provider()
        ).get_historical_price_data()

        return price_data
