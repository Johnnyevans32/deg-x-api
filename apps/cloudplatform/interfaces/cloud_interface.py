from enum import Enum
from typing import Any
from pydantic import BaseModel


class CloudProvider(str, Enum):
    GOOGLE = "google_service"


class UploadFileDTO(BaseModel):
    fileName: str
    data: Any
    authToken: str
    cloudProvider: CloudProvider
