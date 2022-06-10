from enum import Enum
from typing import Union

from pydantic import Field

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.network_interface import Network
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel


class CoinType(str, Enum):
    ERC20 = "erc_20"
    BEP20 = "bep_20"
    ETH = "eth"
    BNB = "bnb"
    BTC = "btc"


class TokenAsset(SBaseModel):
    name: str
    coinType: CoinType
    contractAddress: str
    network: Union[PyObjectId, Network]
    image: str
    blockchain: Union[PyObjectId, Blockchain]
    isLayerOne: bool = Field(default=False)
