from enum import Enum
from typing import Optional
from web3 import Web3

from apps.appclient.services.appclient_service import AppClientService, Apps
from apps.networkfee.interfaces.networkfee_iservice import INetworkFeeService
from apps.networkfee.owlracle.owlracle_type import IGasSpeed, IOwlRacleFeeInfo
from apps.networkfee.types.networkfee_type import TxnSpeedOption
from core.utils.request import REQUEST_METHOD, HTTPRepository
from core.utils.utils_service import timed_cache


class OwlracleSupportedNetwork(str, Enum):
    ETH = "eth"


class OwlracleService(INetworkFeeService):
    appClientService = AppClientService()

    network_gas_limit = {"eth": 21000, "bsc": 90000}

    def __init__(self) -> None:
        client_data = None
        try:
            client_data = self.appClientService.get_client_by_name(Apps.OwlRacle)
        except Exception as e:
            print(e)
        self.api_key = client_data.clientID if client_data else None
        self.api_secret = client_data.clientSecret if client_data else None
        self.base_url = client_data.appUrl if client_data else None
        self.httpRepository = HTTPRepository(self.base_url)

    def name(self) -> str:
        return "owlracle_service"

    @timed_cache(10000000, asyncFunction=True)
    async def get_network_fee_data(
        self, network: str, toBaseConversion: bool = False
    ) -> dict[TxnSpeedOption, IGasSpeed]:
        fee_data = await self.httpRepository.call(
            REQUEST_METHOD.GET,
            f"/v3/{network}/gas?apikey={self.api_key}",
            IOwlRacleFeeInfo,
        )

        def convert_to_eth(value: Optional[float] = None) -> float | None:
            if not value:
                return value
            wei_value = Web3.to_wei(value, "gwei")
            return Web3.from_wei(int(wei_value), "ether").__float__()

        def convert_to_total_gas_fee(gas_price: Optional[float] = None) -> float | None:
            return gas_price * self.network_gas_limit[network] if gas_price else None

        if toBaseConversion:
            fee_data.speeds = list(
                map(
                    lambda speed: IGasSpeed(
                        acceptance=speed.acceptance,
                        maxFeePerGas=convert_to_total_gas_fee(
                            convert_to_eth(speed.maxFeePerGas)
                        ),
                        maxPriorityFeePerGas=convert_to_eth(speed.maxPriorityFeePerGas),
                        baseFee=convert_to_eth(speed.baseFee),
                        gasPrice=convert_to_total_gas_fee(
                            convert_to_eth(speed.gasPrice)
                        ),
                        estimatedFee=speed.estimatedFee,
                    ),
                    fee_data.speeds,
                )
            )
        fee_option_gas_data = {
            TxnSpeedOption.SLOW: fee_data.speeds[0],
            TxnSpeedOption.STANDARD: fee_data.speeds[1],
            TxnSpeedOption.FAST: fee_data.speeds[2],
            TxnSpeedOption.INSTANT: fee_data.speeds[3],
        }

        return fee_option_gas_data

    async def get_fee_value_by_speed(
        self, speed_option: TxnSpeedOption, network: str
    ) -> IGasSpeed:
        fee_data = await self.get_network_fee_data(network)

        return fee_data[speed_option]
