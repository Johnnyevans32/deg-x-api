from typing import List

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from core.utils.helper_service import timed_cache
from core.utils.loggly import logger
from core.utils.model_utility_service import ModelUtilityService


class BlockchainService:
    @timed_cache(10)
    @staticmethod
    def get_blockchains() -> List[Blockchain]:
        logger.info("retrieving blockchains")
        blockchains = ModelUtilityService.find(Blockchain, {"isDeleted": {"$ne": True}})

        return blockchains

    @timed_cache(10)
    @staticmethod
    def get_token_assets(query: dict) -> List[TokenAsset]:
        logger.info(f"retrieving token assets for query - {query}")
        token_assets = ModelUtilityService.find(TokenAsset, query)

        return token_assets
