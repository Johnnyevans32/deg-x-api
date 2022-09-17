from apps.cloudplatform.google.google_service import GoogleService
from apps.cloudplatform.interfaces.cloud_interface import CloudProvider
from apps.cloudplatform.interfaces.cloud_service_interface import ICloudService
from core.utils.loggly import logger


class CloudPlatformRegistry:
    googleService = GoogleService()

    registry: dict[CloudProvider, ICloudService] = {}

    def __init__(self) -> None:
        self.register_services()

    def set_service(self, key: CloudProvider, service: ICloudService) -> None:
        logger.info(f"cloud service registed key - {key}")
        self.registry[key] = service

    def register_services(self) -> None:
        logger.info("lending service registering")
        self.set_service(self.googleService.name(), self.googleService)

    def get_service(self, key: CloudProvider) -> ICloudService:
        return self.registry[key]
