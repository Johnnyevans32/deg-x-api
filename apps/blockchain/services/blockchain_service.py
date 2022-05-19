from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.blockchain.services.blockchain_registry_service import BlockchainRegistry
from apps.user.interfaces.user_interface import User

# from core.utils.helper_service import timed_cache
from core.utils.loggly import logger
from core.utils.model_utility_service import ModelUtilityService


class BlockchainService:
    blockchainRegistry = BlockchainRegistry()

    # @timed_cache(10)
    @staticmethod
    def get_blockchains() -> list[Blockchain]:
        logger.info("retrieving blockchains")
        blockchains = ModelUtilityService.find(Blockchain, {"isDeleted": {"$ne": True}})

        return blockchains

    # @timed_cache(10)
    @staticmethod
    def get_token_assets(query: dict) -> list[TokenAsset]:
        logger.info(f"retrieving token assets for query - {query}")
        token_assets = ModelUtilityService.find(TokenAsset, query)

        return token_assets

    def create_address(self, blockchain_provider: str, mnemonic: str):
        return self.blockchainRegistry.get_service(blockchain_provider).create_address(
            mnemonic
        )

    def send(self, user: User, toAddress: str):
        pass
