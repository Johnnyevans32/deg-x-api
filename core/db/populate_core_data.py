from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.network_interface import Network, NetworkType
from apps.blockchain.interfaces.tokenasset_interface import CoinType, TokenAsset
from core.utils.model_utility_service import ModelUtilityService
from core.utils.loggly import logger


def populate_blockchains():
    data = [
        {"name": "ethereum", "registryName": "ethereum_service", "meta": {}},
        {"name": "bitcoin", "registryName": "bitcoin_service", "meta": {}},
    ]
    mapped_data = list(map(lambda blc: Blockchain(**blc), data))
    map(
        lambda d: ModelUtilityService.model_find_one_and_update(
            Blockchain,
            {"registryName": d.registryName},
            d.dict(by_alias=True, exclude_none=True),
            True,
        ),
        mapped_data,
    )


def populate_networks():
    data = [
        {
            "name": "kovan",
            "networkType": NetworkType.TESTNET,
            "blockchain": ModelUtilityService.find_one(
                Blockchain, {"registryName": "ethereum_service"}, True
            ).id,
            "blockExplorerUrl": "https://kovan.etherscan.io/",
            "apiExplorer": {
                "url": "https://api-kovan.etherscan.io/api",
                "keyToken": "VTQN3HINP8JJND9CEQR7UXK3KX5BFTSVE1",
            },
            "isDefault": True,
            "providerUrl": "https://kovan.infura.io/v3/675849285dfa4748868f4a19b72bfb50",
        }
    ]

    mapped_data = list(map(lambda nt: Network(**nt), data))
    map(
        lambda nt: ModelUtilityService.model_find_one_and_update(
            Network,
            {"name": nt.name},
            nt.dict(by_alias=True, exclude_none=True),
            True,
        ),
        mapped_data,
    )


def populate_tokenassets():
    data = [
        {
            "blockchain": ModelUtilityService.find_one(
                Blockchain, {"registryName": "ethereum_service"}, True
            ).id,
            "code": "ETH",
            "coinType": CoinType.ETH,
            "isLayerOne": True,
            "name": "ethereum",
            "image": "https://cryptologos.cc/logos/ethereum-eth-logo.svg?v=017",
        }
    ]

    mapped_data = list(map(lambda ta: TokenAsset(**ta), data))
    map(
        lambda ta: ModelUtilityService.model_find_one_and_update(
            TokenAsset,
            {"name": ta.name},
            ta.dict(by_alias=True, exclude_none=True),
            True,
        ),
        mapped_data,
    )


def seed_deg_x():
    logger.info("SEEDING BLOCKCHAINS.....")
    populate_blockchains()
    logger.info("SEEDED BLOCKCHAINS!!!")
    logger.info("SEEDING NETWORKS.....")
    populate_networks()
    logger.info("SEEDED NETWORKS!!!")
    logger.info("SEEDING ASSETS.....")
    populate_tokenassets()
    logger.info("SEEDED ASSETS!!!")
