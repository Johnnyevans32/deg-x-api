from apps.defi.interfaces.defiprovider_interface import DefiProvider
from apps.defi.lending.aave.aave_interface import IReserveTokens


class BaseLendingService:
    def get_reserve_assets(
        self,
        defi_provider: DefiProvider,
    ) -> list[IReserveTokens]:
        pass
