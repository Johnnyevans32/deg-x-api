from enum import Enum
from typing import Optional
from pydantic import BaseModel
from core.utils.aes import EncryptedDTO


class CloudProvider(str, Enum):
    GOOGLE = "google_service"


class IDType(str, Enum):
    IDToken = "idtoken"
    AccessToken = "accesstoken"


class BackupSeedPhraseDTO(BaseModel):
    fileName: str
    data: Optional[EncryptedDTO]
    authToken: str
    password: Optional[str]
    cloudProvider: CloudProvider
