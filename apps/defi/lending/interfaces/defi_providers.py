from pydantic import HttpUrl

from core.depends.model import SBaseModel


class DefiProvider(SBaseModel):
    name: str
    contractAddress: str
    blockExplorerUrl: HttpUrl
    serviceName: str
