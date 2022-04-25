from typing import Union

from bson import ObjectId
from pydantic import Field

from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.user.interfaces.user_interface import User
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel
from core.utils.loggly import logger


class WalletAsset(SBaseModel):
    asset: Union[PyObjectId, TokenAsset]
    user: Union[PyObjectId, User]
    wallet: PyObjectId

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
