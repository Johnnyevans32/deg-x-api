from apps.defi.interfaces.defi_provider_interface import DefiProvider


class BaseLendingService:
    def get_reserved_assets(
        self,
        defi_provider: DefiProvider,
    ):
        pass
