from apps.defi.interfaces.defiprovider_interface import DefiProvider
from apps.defi.lending.types.lending_types import IReserveToken


class BaseLendingService:
    def get_reserve_assets(
        self,
        defi_provider: DefiProvider,
    ) -> list[IReserveToken]:
        pass
