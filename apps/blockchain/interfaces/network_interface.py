from enum import Enum
from typing import Optional, Union

from pydantic import HttpUrl

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from core.depends.get_object_id import PyObjectId
from core.depends.model import HashableBaseModel, SBaseModel


class NetworkType(str, Enum):
    MAINNET = "mainnet"
    TESTNET = "testnet"


class ApiExplorer(HashableBaseModel):
    url: Optional[HttpUrl]
    keyToken: Optional[str]


class Network(SBaseModel):
    name: str
    chainId: Optional[str]
    networkType: NetworkType
    blockchain: Union[PyObjectId, Blockchain]
    blockExplorerUrl: Optional[HttpUrl]
    apiExplorer: Optional[ApiExplorer]
    isDefault: bool
    faucetUrl: Optional[HttpUrl]
    providerUrl: Optional[HttpUrl]
