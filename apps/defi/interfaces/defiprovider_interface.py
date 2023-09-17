from enum import Enum
from typing import Any, Optional, Union

from pydantic import Field

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.network_interface import (
    Network,
    NetworkOut,
    NetworkType,
)
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel, SBaseOutModel


class DefiServiceType(str, Enum):
    LENDING = "lending"
    SWAP = "swap"


class DefiProviderOut(SBaseOutModel):
    name: str
    desc: Optional[str]
    tags: Optional[list[str]]
    logo: Optional[str]
    website: Optional[str]
    serviceType: DefiServiceType
    isEnabled: bool = Field(default=True)
    network: Union[PyObjectId, NetworkOut]


class DefiProvider(DefiProviderOut, SBaseModel):
    meta: Optional[Any]
    serviceName: str
    contractAddress: str
    isDefault: bool = Field(default=False)
    blockchain: Union[PyObjectId, Blockchain]
    network: Union[PyObjectId, Network]
    networkType: NetworkType
