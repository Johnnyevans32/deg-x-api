from enum import Enum
from typing import Any
from core.depends.model import SBaseModel, SBaseOutModel


class ChainServiceName(str, Enum):
    BNB = "bnb_service"
    BSC = "bsc_service"
    DOGE = "dogecoin_service"
    BTC = "bitcoin_service"
    ETH = "ethereum_service"
    XTZ = "tezos_service"
    SOL = "solana_service"
    LTC = "litecoin_service"
    DASH = "dashcoin_service"
    AVAX = "avalanche_service"
    MATIC = "polygon_service"
    TRON = "tron_service"


class BlockchainOut(SBaseOutModel):
    name: str
    symbol: str


class Blockchain(BlockchainOut, SBaseModel):
    registryName: ChainServiceName
    meta: dict[str, Any]
