from enum import Enum
from typing import List, Optional, Union

from bson import ObjectId

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.walletasset_interface import WalletAsset
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel
from core.utils.loggly import logger
from core.utils.model_utility_service import ModelUtilityService


class WalletType(str, Enum):
    multichain = "multichain"
    singlechain = "singlechain"


class Wallet(SBaseModel):
    name: str
    user: Union[PyObjectId, User]
    walletType: WalletType
    blockchain: Optional[Union[PyObjectId, Blockchain]]
    address: Optional[str]
    mnemonic: Optional[str]

    @property
    def assets(self) -> List[WalletAsset]:
        walletassets = ModelUtilityService.find(
            WalletAsset, {"wallet": self.id, "isDeleted": False}
        )

        return walletassets

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
