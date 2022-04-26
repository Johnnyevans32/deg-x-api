from apps.blockchain.ethereum.ethereum_service import EthereumService
from apps.blockchain.types.blockchain_service_interface import IBlockchainService
from core.utils.loggly import logger


class BlockchainRegistry:
    ethereumService = EthereumService()

    services: dict[str, IBlockchainService] = {}

    def __init__(self) -> None:
        self.register_services()

    def set_service(self, key: str, service: IBlockchainService):
        logger.info(f"network chain registed key - {key}")
        self.services[key] = service

    def register_services(self) -> None:
        logger.info("network chain registering")
        self.set_service(self.ethereumService.name(), self.ethereumService)

    def get_service(self, key: str) -> IBlockchainService:
        return self.services[key]
