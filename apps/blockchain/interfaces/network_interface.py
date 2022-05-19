from enum import Enum
from typing import Union

from pydantic import HttpUrl


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
    blockExplorerUrl: HttpUrl
