from apps.networkfee.owlracle.owlracle_type import IGasSpeed
from apps.networkfee.registry.networkfee_registry_service import (
    NetworkFeeRegistry,
)
from apps.networkfee.types.networkfee_type import TxnSpeedOption


class NetworkFeeService:
    networkFeeRegistry = NetworkFeeRegistry()

    def get_default_tracker_provider(self) -> str:
        return "owlracle_service"

    async def get_network_fee_data(
        self, network: str, toBaseConversion: bool = False
    ) -> dict[TxnSpeedOption, IGasSpeed]:
        tracker_service = self.networkFeeRegistry.get_service(
            self.get_default_tracker_provider()
        )

        fee_data = await tracker_service.get_network_fee_data(network, toBaseConversion)
        return fee_data

    async def get_fee_value_by_speed(
        self, speed_option: TxnSpeedOption, network: str
    ) -> IGasSpeed:
        tracker_service = self.networkFeeRegistry.get_service(
            self.get_default_tracker_provider()
        )

        fee_data = await tracker_service.get_fee_value_by_speed(speed_option, network)
        return fee_data
