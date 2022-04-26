from enum import Enum
from typing import Union

from bson import ObjectId

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel


class NetworkType(str, Enum):
    Mainnet = "mainnet"
    Testnet = "testnet"


class Network(SBaseModel):
    name: str
    chainId: str
    networkType: NetworkType
    blockchain: Union[PyObjectId, Blockchain]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
