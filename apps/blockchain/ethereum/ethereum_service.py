from eth_account import Account
from web3 import Web3

from web3.middleware import geth_poa_middleware
from apps.blockchain.types.blockchain_service_interface import IBlockchainService
from core.config import settings


class EthereumService(IBlockchainService):
    def name(self) -> str:
        return "ethereum_service"

    def get_network_provider(self):
        web3 = Web3(Web3.HTTPProvider(settings.WEB3_HTTP_PROVIDER))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        return web3

    def create_address(self, mnemonic: str) -> str:
        Account.enable_unaudited_hdwallet_features()
        acct = Account.from_mnemonic(mnemonic)
        return acct.address

    def send(self, from_address: str, to: str, value: int):
        web3 = self.get_network_provider()
        nonce = web3.eth.getTransactionCount(from_address)

        # build a transaction in a dictionary
        tx = {
            "nonce": nonce,
            "to": to,
            "value": web3.toWei(value, "ether"),
            "gas": 2000000,
            "gasPrice": web3.toWei("50", "gwei"),
        }

        # sign the transaction
        signed_tx = web3.eth.account.sign_transaction(tx, "private_key1")

        # send transaction
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        # get transaction hash
        print(web3.toHex(tx_hash))

    def get_balance(self, address: str):
        web3 = self.get_network_provider()
        balance = web3.eth.get_balance(address)
        return balance
