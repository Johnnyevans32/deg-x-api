import abc
from enum import Enum
from typing import Any


class StreamProvider(str, Enum):
    MORALIS = "moralis"


class IStreamService(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: Any) -> Any:
        return (
            hasattr(subclass, "name")
            and callable(subclass.load_data_source)
            or NotImplemented
        )

    @abc.abstractmethod
    def name(self) -> StreamProvider:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_address_stream(
        self,
        address: str,
    ) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    async def handle_stream_data(self, payload: Any) -> Any:
        raise NotImplementedError
