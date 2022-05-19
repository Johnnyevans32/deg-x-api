from apps.defi.lending.aave.aave_service import AaveService
from apps.defi.lending.types.lending_service_interface import ILendingService
from core.utils.loggly import logger


class LendingRegistry:
    aaveService = AaveService()

    services: dict[str, ILendingService] = {}

    def __init__(self) -> None:
        self.register_services()

    def set_service(self, key: str, service: ILendingService):
        logger.info(f"lending service registed key - {key}")
        self.services[key] = service

    def register_services(self) -> None:
        logger.info("lending service registering")
        self.set_service(self.aaveService.name(), self.aaveService)

    def get_service(self, key: str) -> ILendingService:
        return self.services[key]
