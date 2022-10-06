from apps.blockchain.interfaces.blockchain_interface import ChainServiceName
from apps.blockchain.evm_chains.base_eth_service import BaseEvmService


class BscService(BaseEvmService):
    def __init__(self) -> None:
        super().__init__(ChainServiceName.BSC)
