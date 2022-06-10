from typing import Any

import pendulum
from eth_account import Account
from pydantic import parse_obj_as
from web3 import Web3
from web3.middleware import geth_poa_middleware

from apps.blockchain.interfaces.network_interface import Network
from apps.blockchain.interfaces.transaction_interface import (
    BlockchainTransaction,
    TxnSource,
    TxnStatus,
    TxnType,
)
from apps.blockchain.types.blockchain_service_interface import IBlockchainService
from apps.blockchain.types.ethereum_types import (
    EtherscanBaseResponse,
    IEtherscanNormalTxns,
)
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from core.utils.request import HTTPRepository


class EthereumService(IBlockchainService, HTTPRepository):
    def name(self) -> str:
        return "ethereum_service"

    @staticmethod
    def get_network_provider(chain_network: Network):
        web3 = Web3(Web3.HTTPProvider(chain_network.providerUrl))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        return web3

    def create_address(self, mnemonic: str) -> str:
        Account.enable_unaudited_hdwallet_features()
        acct = Account.from_mnemonic(mnemonic)
        return acct.address

    def send(
        self,
        from_address: str,
        to: str,
        value: int,
        chain_network: Network,
        gas=2000000,
        gas_price="50",
    ):
        web3 = self.get_network_provider(chain_network)
        nonce = web3.eth.getTransactionCount(from_address)

        # build a transaction in a dictionary
        tx = {
            "nonce": nonce,
            "to": to,
            "value": web3.toWei(value, "ether"),
            "gas": gas,
            "gasPrice": web3.toWei(gas_price, "gwei"),
        }

        # sign the transaction
        signed_tx = web3.eth.account.sign_transaction(tx, "private_key1")

        # send transaction
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        # get transaction hash
        print(web3.toHex(tx_hash))

    def get_balance(
        self,
        address: str,
        chain_network: Network,
    ):
        web3 = self.get_network_provider(chain_network)
        balance = web3.eth.get_balance(address)
        return balance

    def get_transactions(
        self,
        address: str,
        user: User,
        wallet: Wallet,
        chain_network: Network,
        start_block=0,
    ) -> list[Any]:
        end_block = 999999999999999
        res = self.call(
            "GET",
            f"{chain_network.apiExplorer.url}?module=account&action=txlist&"
            f"address={address}&startblock={start_block}&endblock={end_block}"
            f"&page=1&offset=10000&sort=asc&apikey={chain_network.apiExplorer.keyToken}",
            EtherscanBaseResponse,
        )
        txns_result = parse_obj_as(list[IEtherscanNormalTxns], res.result)

        txn_obj = list(
            map(
                lambda txn: BlockchainTransaction(
                    **{
                        "transactionHash": txn.hash,
                        "fromAddress": txn.fromAddress,
                        "toAddress": txn.to or txn.contractAddress,
                        "gasPrice": txn.gasPrice,
                        "blockNumber": int(txn.blockNumber or 0),
                        "gasUsed": txn.gasUsed,
                        "blockConfirmations": int(txn.confirmations or 0),
                        "network": chain_network.id,
                        "wallet": wallet.id,
                        "amount": float(Web3.fromWei(int(txn.value or 0), "ether")),
                        "status": (
                            TxnStatus.FAILED
                            if (txn.isError == "1")
                            else TxnStatus.SUCCESS
                        ),
                        "isContractExecution": txn.contractAddress != "",
                        "txnType": (
                            TxnType.DEBIT
                            if (txn.fromAddress == address.lower())
                            else TxnType.CREDIT
                        ),
                        "user": user.id,
                        "transactedAt": pendulum.from_timestamp(int(txn.timeStamp)),
                        "source": TxnSource.EXPLORER,
                        "metaData": txn.dict(by_alias=True),
                    }
                ).dict(by_alias=True, exclude_none=True),
                txns_result,
            )
        )
        return txn_obj
