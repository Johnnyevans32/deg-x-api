import abc

from apps.defi.interfaces.defi_provider_interface import DefiProvider
from apps.defi.lending.interfaces.lending_interface import InterestRateMode


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
    def get_user_account_data(self, user: bytes, defi_provider: DefiProvider):
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_config(self, user: bytes, defi_provider: DefiProvider):
        raise NotImplementedError

    @abc.abstractmethod
    def deposit(
        self,
        asset: bytes,
        amount: int,
        on_behalf_of: bytes,
        defi_provider: DefiProvider,
        referral_code=0,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def borrow(
        self,
        asset: bytes,
        amount: float,
        interest_rate_mode: InterestRateMode,
        on_behalf_of: bytes,
        defi_provider: DefiProvider,
        referral_code=0,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def repay(
        self,
        asset: bytes,
        amount: float,
        rate_mode: int,
        on_behalf_of: bytes,
        defi_provider: DefiProvider,
    ):
        raise NotImplementedError
