from apps.blockchain.interfaces.blockchain_interface import ChainServiceName
from apps.blockchain.bitcoin.base_coin_service import BasecoinService


class LitecoinService(BasecoinService):
    def __init__(self) -> None:
        super().__init__("XLT", "LTC", ChainServiceName.LTC)
