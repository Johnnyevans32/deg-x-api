from enum import Enum
from typing import Optional, Union

from pydantic import HttpUrl
from apps.blockchain.interfaces.blockchain_interface import Blockchain

from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel


class NetworkType(str, Enum):
    MAINNET = "mainnet"
    TESTNET = "testnet"


class ApiExplorer(SBaseModel):
    url: HttpUrl
    keyToken: str


class Network(SBaseModel):
    name: str
    chainId: Optional[str]
    networkType: NetworkType
    blockchain: Union[PyObjectId, Blockchain]
    blockExplorerUrl: Optional[HttpUrl]
    apiExplorer: ApiExplorer
    isDefault: bool
    providerUrl: HttpUrl
