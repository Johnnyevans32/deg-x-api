from typing import Any, Callable
from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.network_interface import Network, NetworkType
from apps.blockchain.interfaces.tokenasset_interface import CoinType, TokenAsset
from apps.defi.interfaces.defi_provider_interface import DefiProvider, DefiServiceType
from core.depends.get_object_id import PyObjectId
from core.utils.loggly import logger
from core.utils.model_utility_service import ModelUtilityService

id_or_none: Callable[[Any], PyObjectId | None] = (
    lambda result: result.id if result is not None else None
)


def populate_blockchains():
    data = [
        {"name": "ethereum", "registryName": "ethereum_service", "meta": {}},
        {"name": "bitcoin", "registryName": "bitcoin_service", "meta": {}},
    ]
    mapped_data = list(map(lambda blc: Blockchain(**blc), data))
    list(
        map(
            lambda d: ModelUtilityService.model_find_one_and_update(
                Blockchain,
                {"registryName": d.registryName},
                d.dict(by_alias=True, exclude_none=True),
                True,
            ),
            mapped_data,
        )
    )


def populate_networks():
    data = [
        {
            "name": "kovan",
            "networkType": NetworkType.TESTNET,
            "blockchain": id_or_none(
                ModelUtilityService.find_one(
                    Blockchain,
                    {"registryName": "ethereum_service"},
                )
            ),
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
    list(
        map(
            lambda nt: ModelUtilityService.model_find_one_and_update(
                Network,
                {"name": nt.name},
                nt.dict(by_alias=True, exclude_none=True),
                True,
            ),
            mapped_data,
        )
    )


def populate_tokenassets():
    data = [
        {
            "blockchain": id_or_none(
                ModelUtilityService.find_one(
                    Blockchain, {"registryName": "ethereum_service"}
                )
            ),
            "code": "ETH",
            "coinType": CoinType.ETH,
            "isLayerOne": True,
            "name": "ethereum",
            "image": "https://cryptologos.cc/logos/ethereum-eth-logo.svg?v=017",
        }
    ]

    mapped_data = list(map(lambda ta: TokenAsset(**ta), data))
    list(
        map(
            lambda ta: ModelUtilityService.model_find_one_and_update(
                TokenAsset,
                {"name": ta.name},
                ta.dict(by_alias=True, exclude_none=True),
                True,
            ),
            mapped_data,
        )
    )


def populate_defi_providers():
    data = [
        {
            "name": "aave",
            "contractAddress": "0xE0FBA4FC209B4948668006B2BE61711B7F465BAE",
            "serviceType": DefiServiceType.LENDING,
            "serviceName": "aave_service",
            "isDefault": True,
            "blockchain": id_or_none(
                ModelUtilityService.find_one(
                    Blockchain, {"registryName": "ethereum_service"}
                )
            ),
            "meta": {
                "ProtocolDataProvider": {
                    "address": "0x3c73A5E5785cAC854D468F727c606C07488a29D6"
                }
            },
            "network": id_or_none(
                ModelUtilityService.find_one(Network, {"name": "kovan"})
            ),
        }
    ]

    mapped_data = list(map(lambda dp: DefiProvider(**dp), data))
    list(
        map(
            lambda dp: ModelUtilityService.model_find_one_and_update(
                DefiProvider,
                {"name": dp.name},
                dp.dict(by_alias=True, exclude_none=True),
                True,
            ),
            mapped_data,
        )
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
    populate_defi_providers()
