from apps.blockchain.interfaces.tokenasset_interface import TokenAsset

# from apps.blockchain.interfaces.transaction_interface import BlockchainTransaction
from apps.blockchain.types.blockchain_service_interface import IBlockchainService
from core.utils.request import HTTPRepository


class BitcoinService(IBlockchainService, HTTPRepository):
    def name(self) -> str:
        return "bitcoin_service"

    def get_network_provider(self):
        pass

    def create_address(self, mnemonic: str) -> str:
        pass

    def send(
        self,
        from_address: str,
        to: str,
        value: float,
        token_asset: TokenAsset,
        private_key: str,
        gas=2000000,
        gas_price="50",
    ):
        pass

    def get_balance(
        self,
        address: str,
        token_asset: TokenAsset,
    ):
        pass

    # def get_transactions(
    #     self, address: str, chain_network: Network, start_block=0
    # ) -> list[BlockchainTransaction]:
    #     pass
