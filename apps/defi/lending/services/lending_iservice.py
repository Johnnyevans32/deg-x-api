import abc
from typing import Any

from apps.defi.interfaces.defiprovider_interface import DefiProvider
from apps.defi.lending.types.lending_types import IReserveToken, IUserAcccountData
from apps.defi.lending.interfaces.lending_request_interface import InterestRateMode


class ILendingService(metaclass=abc.ABCMeta):
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
    async def get_user_account_data(
        self, user: str, defi_provider: DefiProvider
    ) -> IUserAcccountData:
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_config(self, user: str, defi_provider: DefiProvider) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    async def deposit(
        self,
        asset: str,
        amount: float,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
    ) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def borrow(
        self,
        asset: str,
        amount: float,
        interest_rate_mode: InterestRateMode,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
    ) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def repay(
        self,
        asset: str,
        amount: float,
        rate_mode: InterestRateMode,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
    ) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def withdraw(
        self,
        asset: str,
        amount: float,
        to: str,
        defi_provider: DefiProvider,
        mnemonic: str,
    ) -> str:
        raise NotImplementedError

    async def get_reserve_assets(
        self,
        defi_provider: DefiProvider,
    ) -> list[IReserveToken]:
        pass
