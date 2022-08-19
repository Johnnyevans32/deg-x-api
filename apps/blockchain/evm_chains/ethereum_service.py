from apps.blockchain.interfaces.blockchain_interface import ChainServiceName
from apps.blockchain.services.base_eth_service import BaseEvmService


class EthereumService(BaseEvmService):
    def __init__(self) -> None:
        super().__init__(ChainServiceName.ETH)
