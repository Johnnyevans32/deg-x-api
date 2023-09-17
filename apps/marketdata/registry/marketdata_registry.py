from apps.marketdata.coingecko.coingecko_service import CoingeckoService
from apps.marketdata.coinmarket.coinmarket_service import CoinmarketService
from apps.marketdata.services.marketdata_iservice import IMarketDataService
from core.utils.loggly import logger


class MarketDataRegistry:
    coinmarketService = CoinmarketService()
    coingeckoService = CoingeckoService()

    registry: dict[str, IMarketDataService] = {}

    def __init__(self) -> None:
        self.register_services()

    def set_service(self, key: str, service: IMarketDataService) -> None:
        logger.info(f"market data service registed key - {key}")
        self.registry[key] = service

    def register_services(self) -> None:
        logger.info("market data service registering")
        self.set_service(self.coinmarketService.name(), self.coinmarketService)
        self.set_service(self.coingeckoService.name(), self.coingeckoService)

    def get_service(self, key: str) -> IMarketDataService:
        return self.registry[key]
