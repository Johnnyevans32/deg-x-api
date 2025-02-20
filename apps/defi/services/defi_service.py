from apps.defi.interfaces.defiprovider_interface import DefiProvider
from apps.user.interfaces.user_interface import User
from apps.wallet.services.wallet_service import WalletService
from core.utils.custom_exceptions import UnicornException
from core.utils.model_utility_service import ModelUtilityService


class DefiService:
    walletService = WalletService()

    async def get_defi_providers_by_default_network(
        self, user: User
    ) -> list[DefiProvider]:

        user_wallet = await self.walletService.get_user_default_wallet(user)
        defi_providers = await ModelUtilityService.find_and_populate(
            DefiProvider,
            {"networkType": user_wallet.networkType, "isDeleted": False},
            ["network"],
        )

        if not defi_providers:
            raise UnicornException("defi providers type not found for network")

        return defi_providers
