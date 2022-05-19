from enum import Enum
from typing import Optional, Union

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.walletasset_interface import WalletAsset
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel
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
    def assets(self) -> list[WalletAsset]:
        walletassets = ModelUtilityService.find(
            WalletAsset, {"wallet": self.id, "isDeleted": False}
        )

        return walletassets
