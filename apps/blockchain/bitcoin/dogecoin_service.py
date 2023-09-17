from apps.blockchain.interfaces.blockchain_interface import ChainServiceName
from apps.blockchain.bitcoin.base_coin_service import BasecoinService

# from apps.blockchain.services.base_altcoin_service import BaseAltcoinService


class DogecoinService(BasecoinService):
    def __init__(self) -> None:
        super().__init__("XDT", "DOGE", ChainServiceName.DOGE)
