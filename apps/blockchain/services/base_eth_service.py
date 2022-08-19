from typing import Any, cast

import eth_utils
import pendulum
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_typing import Address as EthAddress
from pydantic import parse_obj_as
from web3 import Web3
from web3.contract import AsyncContract
from web3.middleware import geth_poa_middleware

from apps.blockchain.interfaces.blockchain_interface import ChainServiceName
from apps.blockchain.interfaces.network_interface import Network
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
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
from apps.wallet.interfaces.walletasset_interface import Address
from core.utils.loggly import logger
from core.utils.request import HTTPRepository
from core.utils.utils_service import Utils, timed_cache


class BaseEvmService(IBlockchainService, HTTPRepository):
    def __init__(self, service_name: ChainServiceName) -> None:
        self.service_name = service_name

    def name(self) -> ChainServiceName:
        return self.service_name

    @staticmethod
    async def get_network_provider(chain_network: Network):
        logger.info("getting network rpc provider")
        web3 = Web3(Web3.HTTPProvider(chain_network.providerUrl))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        return web3

    @timed_cache(60, 10)
    @staticmethod
    def get_erc20_contract_obj(crt_address: str, web3: Web3) -> AsyncContract:
        address = eth_utils.to_bytes(hexstr=crt_address)
        abi = Utils.get_compiled_sol("IERC20", "0.6.12")
        erc20_crt = cast(
            AsyncContract, web3.eth.contract(address=EthAddress(address), abi=abi)
        )

        return erc20_crt

    @staticmethod
    def get_account_by_mmenonic(mnemonic: str) -> LocalAccount:
        Account.enable_unaudited_hdwallet_features()
        account: LocalAccount = Account.from_mnemonic(mnemonic)
        return account

    async def create_address(self, mnemonic: str) -> Address:
        account = self.get_account_by_mmenonic(mnemonic)
        return Address(**{"main": account.address})

    async def send(
        self,
        address_obj: Address,
        to: str,
        value: float,
        token_asset: TokenAsset,
        mnemonic: str,
        gas=21000,
        gas_price=1,
    ):
        chain_network = cast(Network, token_asset.network)
        web3 = await BaseEvmService.get_network_provider(chain_network)
        from_address = address_obj.main
        nonce = web3.eth.get_transaction_count(from_address)
        txn_miner_tip = web3.eth.max_priority_fee + Web3.toWei(100, "gwei")
        block_base_fee_per_gas = web3.eth.get_block("latest").get("baseFeePerGas")
        if token_asset.contractAddress:
            erc20_crt = BaseEvmService.get_erc20_contract_obj(
                token_asset.contractAddress, web3
            )

            txn_build = erc20_crt.functions.transfer(
                eth_utils.to_bytes(hexstr=to), Web3.toWei(value, "ether")
            ).build_transaction({"nonce": nonce})

        else:
            # build a transaction in a dictionary
            txn_build = {
                "nonce": nonce,
                "to": eth_utils.to_bytes(hexstr=to),
                "value": Web3.toWei(value, "ether"),
            }

        txn_build = {
            **txn_build,
            "maxPriorityFeePerGas": txn_miner_tip,
            "gas": web3.eth.estimate_gas(txn_build),
            "chainId": web3.eth.chain_id,
            "maxFeePerGas": block_base_fee_per_gas + txn_miner_tip,
        }

        txn_hash = await self.sign_txn(web3, mnemonic, txn_build)

        return txn_hash

    async def get_balance(
        self,
        address_obj: Address,
        token_asset: TokenAsset,
    ):
        chain_network = cast(Network, token_asset.network)
        address = address_obj.main
        web3 = await BaseEvmService.get_network_provider(chain_network)
        if token_asset.contractAddress:
            erc20_crt = BaseEvmService.get_erc20_contract_obj(
                token_asset.contractAddress, web3
            )
            balance = erc20_crt.functions.balanceOf(
                eth_utils.to_bytes(hexstr=address)
            ).call()
        else:
            balance = web3.eth.get_balance(address)
        return Web3.fromWei(int(balance), "ether")

    async def sign_txn(
        self,
        web3: Web3,
        mnemonic: str,
        txn_build: Any,
    ) -> str:
        # sign the transaction
        account = self.get_account_by_mmenonic(mnemonic)
        signed_tx = account.sign_transaction(txn_build)
        print("txn_build", txn_build)

        # send transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return str(Web3.toHex(tx_hash))

    async def approve_erc_20_txns(
        self,
        token_contract_address: str,
        web3: Web3,
        spender: str,
        amount: float,
        mnemonic: str,
        gas=None,
        gas_price=None,
    ):
        account = self.get_account_by_mmenonic(mnemonic)
        erc20_crt = BaseEvmService.get_erc20_contract_obj(token_contract_address, web3)
        nonce = web3.eth.get_transaction_count(account.address)

        approve_txn_build = erc20_crt.functions.approve(
            eth_utils.to_bytes(hexstr=spender), Web3.toWei(amount, "ether")
        ).build_transaction({"nonce": nonce})

        txn_hash = await self.sign_txn(web3, mnemonic, approve_txn_build)

        return txn_hash

    async def get_transactions(
        self,
        address_obj: Address,
        user: User,
        wallet: Wallet,
        chain_network: Network,
        start_block=0,
    ) -> list[Any]:
        assert chain_network.apiExplorer, "network apiexplorer not found"
        end_block = 999999999999999
        address = address_obj.main
        res = await self.call(
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

    async def swap_between_wraps(
        self,
        value: float,
        mnemonic: str,
        token_asset: TokenAsset,
    ):
        pass
