from apps.chainstream.interfaces.stream_service_interface import (
    IStreamService,
    StreamProvider,
)
from apps.chainstream.moralis.moralis_service import MoralisService

from core.utils.loggly import logger


class StreamRegistry:
    moralisService = MoralisService()
    registry: dict[StreamProvider, IStreamService] = {}

    def __init__(self) -> None:
        self.register_services()

    def set_service(self, key: StreamProvider, service: IStreamService) -> None:
        logger.info(f"chain stream service registed key - {key}")
        self.registry[key] = service

    def register_services(self) -> None:
        logger.info("chain stream service registering")
        self.set_service(self.moralisService.name(), self.moralisService)

    def get_service(self, key: StreamProvider) -> IStreamService:
        return self.registry[key]
