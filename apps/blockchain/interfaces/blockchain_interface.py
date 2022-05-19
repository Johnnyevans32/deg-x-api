from typing import Any

from core.depends.model import SBaseModel


class Blockchain(SBaseModel):
    name: str
    registryName: str
    meta: dict[str, Any]
