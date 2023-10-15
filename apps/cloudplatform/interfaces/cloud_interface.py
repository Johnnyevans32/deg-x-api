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
    data: Optional[EncryptedDTO] = None
    seed: Optional[str] = None
    authToken: str
    password: Optional[str] = None
    cloudProvider: CloudProvider
