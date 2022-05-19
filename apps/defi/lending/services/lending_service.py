import eth_utils

from apps.defi.lending.services.lending_registry import LendingRegistry

# from apps.user.interfaces.user_interface import User


class LendingService:

    lendingRegistry = LendingRegistry()

    def get_user_lending_data(
        self, address: str = "0xcc5da237b28799725bb15339aCA7f0097329a75D"
    ):
        user_lending_data = self.lendingRegistry.get_service(
            "aave"
        ).get_user_account_data(eth_utils.to_bytes(hexstr=address))

        return user_lending_data

    def get_user_config(
        self, address: str = "0xcc5da237b28799725bb15339aCA7f0097329a75D"
    ):
        user_config_data = self.lendingRegistry.get_service("aave").get_user_config(
            eth_utils.to_bytes(hexstr=address)
        )

        return user_config_data
