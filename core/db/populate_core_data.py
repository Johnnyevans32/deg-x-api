from typing import Any, Callable

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.network_interface import Network, NetworkType
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.defi.interfaces.defi_provider_interface import DefiProvider, DefiServiceType
from core.depends.get_object_id import PyObjectId
from core.utils.loggly import logger
from core.utils.model_utility_service import ModelUtilityService

id_or_none: Callable[[Any], PyObjectId | None] = (
    lambda result: result.id if result else None
)


async def populate_blockchains():
    data = [
        {"name": "ethereum", "registryName": "ethereum_service", "meta": {}},
        {"name": "bitcoin", "registryName": "bitcoin_service", "meta": {}},
        {"name": "solana", "registryName": "solana_service", "meta": {}},
        {"name": "dogecoin", "registryName": "dogecoin_service", "meta": {}},
        {"name": "binance", "registryName": "binance_service", "meta": {}},
        {"name": "tezos", "registryName": "tezos_service", "meta": {}},
    ]
    mapped_data = list(map(lambda blc: Blockchain(**blc), data))

    for d in mapped_data:
        await ModelUtilityService.model_find_one_and_update(
            Blockchain,
            {"registryName": d.registryName},
            d.dict(by_alias=True, exclude_none=True),
            True,
        ),


async def populate_networks():
    data = [
        {
            "name": "kovan",
            "networkType": NetworkType.TESTNET,
            "blockchain": id_or_none(
                await ModelUtilityService.find_one(
                    Blockchain,
                    {"name": "ethereum"},
                )
            ),
            "blockExplorerUrl": "https://kovan.etherscan.io/",
            "apiExplorer": {
                "url": "https://api-kovan.etherscan.io/api",
                "keyToken": "VTQN3HINP8JJND9CEQR7UXK3KX5BFTSVE1",
            },
            "isDefault": True,
            "providerUrl": "https://kovan.infura.io/v3/675849285dfa4748868f4a19b72bfb50",
        },
        {
            "name": "solanadev",
            "networkType": NetworkType.TESTNET,
            "blockchain": id_or_none(
                await ModelUtilityService.find_one(
                    Blockchain,
                    {"name": "solana"},
                )
            ),
            "blockExplorerUrl": "https://solscan.io/",
            "apiExplorer": {},
            "isDefault": True,
            "providerUrl": "https://api.devnet.solana.com",
        },
    ]

    mapped_data = list(map(lambda nt: Network(**nt), data))
    for nt in mapped_data:
        await ModelUtilityService.model_find_one_and_update(
            Network,
            {"name": nt.name},
            nt.dict(by_alias=True, exclude_none=True),
            True,
        ),


async def populate_tokenassets():
    data = [
        {
            "blockchain": id_or_none(
                await ModelUtilityService.find_one(
                    Blockchain,
                    {"name": "ethereum"},
                )
            ),
            "symbol": "ETH",
            "isLayerOne": True,
            "name": "ethereum",
            "image": "https://cryptologos.cc/logos/ethereum-eth-logo.svg?v=017",
        },
        {
            "blockchain": id_or_none(
                await ModelUtilityService.find_one(
                    Blockchain,
                    {"name": "solana"},
                )
            ),
            "symbol": "SOL",
            "isLayerOne": True,
            "name": "solana",
            "image": "https://cryptologos.cc/logos/ethereum-eth-logo.svg?v=017",
            "network": id_or_none(
                await ModelUtilityService.find_one(Network, {"name": "solanadev"})
            ),
        },
        {
            "blockchain": id_or_none(
                await ModelUtilityService.find_one(
                    Blockchain,
                    {"name": "tezos"},
                )
            ),
            "symbol": "XTZ",
            "isLayerOne": True,
            "name": "tezos",
            "image": "https://cryptologos.cc/logos/ethereum-eth-logo.svg?v=017",
        },
        {
            "blockchain": id_or_none(
                await ModelUtilityService.find_one(
                    Blockchain,
                    {"name": "binance"},
                )
            ),
            "symbol": "BNB",
            "isLayerOne": True,
            "name": "binance coin",
            "image": "https://cryptologos.cc/logos/ethereum-eth-logo.svg?v=017",
        },
        {
            "blockchain": id_or_none(
                await ModelUtilityService.find_one(
                    Blockchain,
                    {"name": "dogecoin"},
                )
            ),
            "symbol": "DOGE",
            "isLayerOne": True,
            "name": "dogecoin",
            "image": "https://cryptologos.cc/logos/ethereum-eth-logo.svg?v=017",
        },
        {
            "blockchain": id_or_none(
                await ModelUtilityService.find_one(
                    Blockchain,
                    {"name": "bitcoin"},
                )
            ),
            "symbol": "BTC",
            "isLayerOne": True,
            "name": "bitcoin",
            "image": "https://cryptologos.cc/logos/ethereum-eth-logo.svg?v=017",
        },
    ]

    mapped_data = list(map(lambda ta: TokenAsset(**ta), data))
    for ta in mapped_data:
        await ModelUtilityService.model_find_one_and_update(
            TokenAsset,
            {"name": ta.name},
            ta.dict(by_alias=True, exclude_none=True),
            True,
        ),


async def populate_defi_providers():
    data = [
        {
            "name": "aave",
            "contractAddress": "0xE0FBA4FC209B4948668006B2BE61711B7F465BAE",
            "serviceType": DefiServiceType.LENDING,
            "serviceName": "aave_service",
            "isDefault": False,
            "blockchain": id_or_none(
                await ModelUtilityService.find_one(Blockchain, {"name": "ethereum"})
            ),
            "meta": {
                "ProtocolDataProvider": {
                    "address": "0x3c73A5E5785cAC854D468F727c606C07488a29D6"
                }
            },
            "networkType": NetworkType.TESTNET,
            "network": id_or_none(
                await ModelUtilityService.find_one(Network, {"name": "kovan"})
            ),
        },
        {
            "name": "solend",
            "contractAddress": "s",
            "serviceType": DefiServiceType.LENDING,
            "serviceName": "solend_service",
            "isDefault": True,
            "blockchain": id_or_none(
                await ModelUtilityService.find_one(Blockchain, {"name": "solana"})
            ),
            "networkType": NetworkType.TESTNET,
            "network": id_or_none(
                await ModelUtilityService.find_one(Network, {"name": "solanadev"})
            ),
        },
    ]

    mapped_data = list(map(lambda dp: DefiProvider(**dp), data))
    for dp in mapped_data:
        await ModelUtilityService.model_find_one_and_update(
            DefiProvider,
            {"name": dp.name},
            dp.dict(by_alias=True, exclude_none=True),
            True,
        ),


async def seed_deg_x():
    logger.info("SEEDING BLOCKCHAINS.....")
    await populate_blockchains()
    logger.info("SEEDED BLOCKCHAINS!!!")
    logger.info("SEEDING NETWORKS.....")
    await populate_networks()
    logger.info("SEEDED NETWORKS!!!")
    logger.info("SEEDING ASSETS.....")
    await populate_tokenassets()
    logger.info("SEEDED ASSETS!!!")
    await populate_defi_providers()
