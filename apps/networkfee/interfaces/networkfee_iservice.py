import abc
from typing import Any
from apps.networkfee.owlracle.owlracle_type import IGasSpeed

from apps.networkfee.types.networkfee_type import TxnSpeedOption


class INetworkFeeService(metaclass=abc.ABCMeta):
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
    async def get_network_fee_data(
        self, network: str, toBaseConversion: bool
    ) -> dict[TxnSpeedOption, IGasSpeed]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_fee_value_by_speed(
        self, speed_option: TxnSpeedOption, network: str
    ) -> IGasSpeed:
        raise NotImplementedError
