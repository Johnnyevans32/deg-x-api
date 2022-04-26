from enum import Enum
from typing import Optional, Union

from bson import ObjectId
from pydantic import Field

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel


class CoinType(str, Enum):
    ERC_20 = "erc_20"
    BEP_20 = "bep_20"
    ETH = "eth"
    BNB = "bnb"
    BTC = "btc"


class TokenAsset(SBaseModel):
    name: str
    code: str
    coinType: CoinType
    contractAddress: Optional[str]
    blockchain: Union[PyObjectId, Blockchain]
    isLayerOne: bool = Field(default=False)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
