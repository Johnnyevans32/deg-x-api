from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel


class CloudProvider(str, Enum):
    GOOGLE = "google_service"


class IDType(str, Enum):
    IDToken = "idtoken"
    AccessToken = "accesstoken"


class UploadFileDTO(BaseModel):
    fileName: str
    data: Optional[Any]
    authToken: str
    cloudProvider: CloudProvider
