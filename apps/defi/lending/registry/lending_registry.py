from apps.defi.lending.aave.aave_service import AaveService
from apps.defi.lending.aave.aave_v3_service import AaveV3Service
from apps.defi.lending.services.lending_service_interface import ILendingService
from apps.defi.lending.solend.solend_service import SolendService

from apps.defi.lending.yupana.yupana_service import YupanaService
from core.utils.loggly import logger


class LendingRegistry:
    aaveService = AaveService()
    aaveV3Service = AaveV3Service()
    solendService = SolendService()
    yupanaService = YupanaService()

    registry: dict[str, ILendingService] = {}

    def __init__(self) -> None:
        self.register_services()

    def set_service(self, key: str, service: ILendingService):
        logger.info(f"lending service registed key - {key}")
        self.registry[key] = service

    def register_services(self) -> None:
        logger.info("lending service registering")
        self.set_service(self.aaveService.name(), self.aaveService)
        self.set_service(self.aaveV3Service.name(), self.aaveV3Service)
        self.set_service(self.solendService.name(), self.solendService)
        self.set_service(self.yupanaService.name(), self.yupanaService)

    def get_service(self, key: str) -> ILendingService:
        return self.registry[key]
