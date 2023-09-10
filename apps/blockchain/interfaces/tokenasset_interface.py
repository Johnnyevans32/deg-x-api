from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field, ConfigDict

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.network_interface import Network, NetworkOut
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel, SBaseOutModel


class CoinType(str, Enum):
    ERC20 = "erc_20"
    BEP20 = "bep_20"
    ETH = "eth"
    BNB = "bnb"
    BTC = "btc"


class TokenAssetCore(BaseModel):
    network: Union[PyObjectId, NetworkOut]
    contractAddress: Optional[str]


class TokenAssetOut(TokenAssetCore, SBaseOutModel):
    name: str
    symbol: str
    image: Optional[str]
    coinGeckoId: Optional[str]

    model_config = ConfigDict(str_strip_whitespace=True, str_to_lower=True)


class TokenAsset(TokenAssetOut, SBaseModel):
    network: Union[PyObjectId, Network]
    blockchain: Union[PyObjectId, Blockchain]
    isLayerOne: bool = Field(default=False)
    hasTestToken: bool = Field(default=False)
