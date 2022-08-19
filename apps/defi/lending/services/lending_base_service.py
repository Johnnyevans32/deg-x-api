from apps.defi.interfaces.defi_provider_interface import DefiProvider


class BaseLendingService:
    def get_reserve_assets(
        self,
        defi_provider: DefiProvider,
    ):
        pass
