from typing import Any
from web3 import Web3

from apps.blockchain.interfaces.blockchain_interface import ChainServiceName, Blockchain
from apps.blockchain.evm_chains.base_eth_service import BaseEvmService

from apps.blockchain.interfaces.network_interface import Network
from apps.networkfee.types.networkfee_type import TxnSpeedOption


class BscService(BaseEvmService):
    def __init__(self) -> None:
        super().__init__(ChainServiceName.BSC)

    async def sign_txn(
        self,
        network: Network,
        blockchain: Blockchain,
        mnemonic: str,
        txn_build: Any,
        txn_speed: TxnSpeedOption = TxnSpeedOption.STANDARD,
    ) -> str:
        # sign the transaction
        web3 = self.get_network_provider(network)
        account = self.get_account_by_mmenonic(mnemonic)
        nonce = web3.eth.get_transaction_count(account.address)
        gas_fee_data = await self.networkFeeService.get_fee_value_by_speed(
            txn_speed, blockchain.symbol
        )
        txn_miner_tip = web3.eth.max_priority_fee + Web3.toWei(10, "gwei")
        maxPFee = gas_fee_data.gasPrice
        assert maxPFee, "bsc gas fee not set"
        txn_build = {
            **txn_build,
            "nonce": nonce,
            "gasPrice": Web3.toWei(maxPFee, "gwei") or txn_miner_tip,
            "gas": web3.eth.estimate_gas(txn_build),
            "chainId": web3.eth.chain_id,
        }

        signed_tx = account.sign_transaction(txn_build)

        # send transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return str(Web3.toHex(tx_hash))
