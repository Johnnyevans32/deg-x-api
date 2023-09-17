import abc
from typing import Any


from apps.marketdata.services.marketdata_type import IPriceData


class IMarketDataService(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: Any) -> Any:
        return (
            hasattr(subclass, "name")
            and callable(subclass.load_data_source)
            or NotImplemented
        )

    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_historical_price_data(self) -> list[IPriceData]:
        raise NotImplementedError
