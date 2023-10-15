from enum import Enum
from typing import Optional, Union


from apps.blockchain.interfaces.blockchain_interface import Blockchain
from core.depends.get_object_id import PyObjectId
from core.depends.model import HashableBaseModel, SBaseModel, SBaseOutModel


class NetworkType(str, Enum):
    MAINNET = "mainnet"
    TESTNET = "testnet"


class ApiExplorer(HashableBaseModel):
    url: Optional[str] = None
    keyToken: Optional[str] = None


class NetworkOut(SBaseOutModel):
    name: str


class Network(NetworkOut, SBaseModel):
    chainId: Optional[str] = None
    networkType: NetworkType
    blockchain: Union[PyObjectId, Blockchain]
    blockExplorerUrl: Optional[str] = None
    apiExplorer: Optional[ApiExplorer] = None
    isDefault: bool
    faucetUrl: Optional[str] = None
    providerUrl: Optional[str] = None
