from enum import Enum
from typing import Optional, Union

from pydantic import Field

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.network_interface import Network
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel, SBaseOutModel


class CoinType(str, Enum):
    ERC20 = "erc_20"
    BEP20 = "bep_20"
    ETH = "eth"
    BNB = "bnb"
    BTC = "btc"


class TokenAssetOut(SBaseOutModel):
    name: str
    symbol: str
    image: str
    # coinType: Optional[CoinType]
    contractAddress: Optional[str]


class TokenAsset(TokenAssetOut, SBaseModel):
    network: Optional[Union[PyObjectId, Network]]
    blockchain: Union[PyObjectId, Blockchain]
    isLayerOne: bool = Field(default=False)
    hasTestToken: bool = Field(default=False)
