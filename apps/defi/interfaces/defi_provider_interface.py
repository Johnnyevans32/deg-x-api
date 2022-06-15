from enum import Enum
from typing import Any, Optional, Union

from pydantic import Field

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.network_interface import Network
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel


class DefiServiceType(str, Enum):
    LENDING = "lending"
    SWAP = "swap"


class DefiProvider(SBaseModel):
    name: str
    contractAddress: str
    isDefault: bool = Field(default=False)
    serviceType: DefiServiceType
    serviceName: str
    blockchain: Union[PyObjectId, Blockchain]
    network: Union[PyObjectId, Network]
    meta: Optional[Any]
