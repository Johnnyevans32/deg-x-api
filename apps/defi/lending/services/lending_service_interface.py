import abc

from apps.defi.interfaces.defi_provider_interface import DefiProvider
from apps.defi.lending.aave.aave_interface import IReserveTokens
from apps.defi.lending.interfaces.lending_request_interface import InterestRateMode


class ILendingService(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "name")
            and callable(subclass.load_data_source)
            or NotImplemented
        )

    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_user_account_data(self, user: str, defi_provider: DefiProvider):
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_config(self, user: str, defi_provider: DefiProvider):
        raise NotImplementedError

    @abc.abstractmethod
    async def deposit(
        self,
        asset: str,
        amount: float,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
    ):
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
    ):
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
    ):
        raise NotImplementedError

    @abc.abstractmethod
    async def withdraw(
        self,
        asset: str,
        amount: int,
        to: str,
        defi_provider: DefiProvider,
        mnemonic: str,
    ) -> float:
        raise NotImplementedError

    async def get_reserve_assets(
        self,
        defi_provider: DefiProvider,
    ) -> list[IReserveTokens]:
        pass
