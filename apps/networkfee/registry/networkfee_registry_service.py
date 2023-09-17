from apps.networkfee.interfaces.networkfee_iservice import INetworkFeeService
from apps.networkfee.owlracle.owlracle_service import OwlracleService
from core.utils.loggly import logger


class NetworkFeeRegistry:
    owlracleService = OwlracleService()
    registry: dict[str, INetworkFeeService] = {}

    def __init__(self) -> None:
        self.register_services()

    def set_service(self, key: str, service: INetworkFeeService) -> None:
        logger.info(f"gas tracker service registed key - {key}")
        self.registry[key] = service

    def register_services(self) -> None:
        logger.info("gas tracker service registering")
        self.set_service(self.owlracleService.name(), self.owlracleService)

    def get_service(self, key: str) -> INetworkFeeService:
        return self.registry[key]
