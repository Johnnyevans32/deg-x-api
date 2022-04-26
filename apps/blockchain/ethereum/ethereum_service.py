from eth_account import Account

from apps.blockchain.types.blockchain_service_interface import IBlockchainService


class EthereumService(IBlockchainService):
    def name(self) -> str:
        return "ethereum_service"

    def create_address(self, mnemonic: str) -> str:
        Account.enable_unaudited_hdwallet_features()
        acct = Account.from_mnemonic(mnemonic)
        return acct.address
