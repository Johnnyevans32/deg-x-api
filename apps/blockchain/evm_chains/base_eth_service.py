from typing import Any, cast

import pendulum
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_typing import Address as EthAddress
from eth_typing import HexStr
from web3 import Web3
from web3.contract.async_contract import AsyncContract
from web3.middleware.geth_poa import geth_poa_middleware
from web3.types import Wei

from apps.blockchain.interfaces.blockchain_interface import Blockchain, ChainServiceName
from apps.blockchain.interfaces.network_interface import Network
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.blockchain.interfaces.transaction_interface import (
    BlockchainTransaction,
    TxnSource,
    TxnStatus,
    TxnType,
)
from apps.blockchain.interfaces.blockchain_iservice import IBlockchainService
from apps.blockchain.types.ethereum_type import (
    EtherscanBaseResponse,
    IEtherscanNormalTxns,
)
from apps.networkfee.services.networkfee_service import (
    NetworkFeeService,
)
from apps.networkfee.types.networkfee_type import TxnSpeedOption

from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from apps.wallet.interfaces.walletasset_interface import Address
from core.depends.get_object_id import PyObjectId
from core.utils.loggly import logger
from core.utils.model_utility_service import ModelUtilityService
from core.utils.request import REQUEST_METHOD, HTTPRepository
from core.utils.utils_service import Utils, timed_cache


class BaseEvmService(IBlockchainService):
    httpRepository = HTTPRepository()
    networkFeeService = NetworkFeeService()

    def __init__(self, service_name: ChainServiceName) -> None:
        self.service_name = service_name

    def name(self) -> ChainServiceName:
        return self.service_name

    def get_network_provider(self, chain_network: Network) -> Web3:
        logger.info("getting network rpc provider")
        web3 = Web3(Web3.HTTPProvider(chain_network.providerUrl))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        return web3

    @staticmethod
    @timed_cache(60, 10, asyncFunction=True)
    async def get_erc20_contract_obj(crt_address: str, web3: Web3) -> AsyncContract:
        address = Web3.to_bytes(hexstr=HexStr(crt_address))
        abi = await Utils.get_compiled_sol("IERC20", "0.6.12")
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
        address = account.address
        return Address(main=address, test=address)

    async def send(
        self,
        address: str,
        to: str,
        value: float,
        token_asset: TokenAsset,
        mnemonic: str,
        gas: int = 21000,
        gas_price: int = 1,
    ) -> str:
        chain_network = cast(Network, token_asset.network)
        blockchain = cast(Blockchain, token_asset.blockchain)
        web3 = self.get_network_provider(chain_network)
        if token_asset.contractAddress:
            erc20_crt = await BaseEvmService.get_erc20_contract_obj(
                token_asset.contractAddress, web3
            )

            txn_build = erc20_crt.functions.transfer(
                Web3.to_bytes(hexstr=HexStr(to)), Web3.to_wei(value, "ether")
            ).build_transaction()

        else:
            # build a transaction in a dictionary
            txn_build = {
                "to": Web3.to_bytes(hexstr=HexStr(to)),
                "value": Web3.to_wei(value, "ether"),
            }

        txn_build = {
            **txn_build,
        }

        txn_hash = await self.sign_txn(chain_network, blockchain, mnemonic, txn_build)

        return txn_hash

    async def get_balance(
        self,
        address: str,
        token_asset: TokenAsset,
    ) -> float:
        chain_network = cast(Network, token_asset.network)

        web3 = self.get_network_provider(chain_network)
        if token_asset.contractAddress:
            erc20_crt = await BaseEvmService.get_erc20_contract_obj(
                token_asset.contractAddress, web3
            )
            balance = erc20_crt.functions.balanceOf(
                Web3.to_bytes(hexstr=HexStr(address))
            ).call()
        else:
            balance = web3.eth.get_balance(
                EthAddress(Web3.to_bytes(hexstr=HexStr(address)))
            )
        return float(Web3.from_wei(int(balance), "ether"))

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
        txn_miner_tip = web3.eth.max_priority_fee + Web3.to_wei(12, "gwei")
        block_base_fee_per_gas = web3.eth.get_block("latest").get("baseFeePerGas")
        maxPFee = gas_fee_data.maxPriorityFeePerGas
        maxFee = gas_fee_data.maxFeePerGas
        assert maxPFee and maxFee, "evm gas fee not set"
        txn_build = {
            **txn_build,
            "nonce": nonce,
            "maxPriorityFeePerGas": Web3.to_wei(maxPFee, "gwei") or txn_miner_tip,
            "gas": web3.eth.estimate_gas(txn_build),
            "chainId": web3.eth.chain_id,
            "maxFeePerGas": cast(
                Wei, (Web3.to_wei(maxFee, "gwei") or block_base_fee_per_gas)
            )
            + txn_miner_tip,
        }

        signed_tx = account.sign_transaction(txn_build)

        # send transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return str(Web3.to_hex(tx_hash))

    async def approve_token_delegation(
        self,
        network: Network,
        blockchain: Blockchain,
        mnemonic: str,
        amount: float,
        token_address: str,
        spender_address: str,
    ) -> str:
        web3 = self.get_network_provider(network)
        erc20_crt = await BaseEvmService.get_erc20_contract_obj(token_address, web3)

        approve_txn_build = erc20_crt.functions.approve(
            Web3.to_bytes(hexstr=HexStr(spender_address)), Web3.to_wei(amount, "ether")
        ).build_transaction()

        txn_hash = await self.sign_txn(network, blockchain, mnemonic, approve_txn_build)

        return txn_hash

    async def get_transactions(
        self,
        address: str,
        user: User,
        wallet: Wallet,
        chain_network: Network,
        start_block: int = 0,
    ) -> list[Any]:
        assert chain_network.apiExplorer, "network apiexplorer not found"
        end_block = 999999999999999

        res = await self.httpRepository.call(
            REQUEST_METHOD.GET,
            f"{chain_network.apiExplorer.url}?module=account&action=txlist&"
            f"address={address}&startblock={start_block}&endblock={end_block}"
            f"&page=1&offset=10000&sort=asc&apikey={chain_network.apiExplorer.keyToken}",
            EtherscanBaseResponse[list[IEtherscanNormalTxns]],
        )
        txns_result = res.result
        txn_obj = []
        for txn in txns_result:
            txn_type = (
                TxnType.DEBIT if txn.fromAddress == address.lower() else TxnType.CREDIT
            )
            # other_user_address = (
            #     txn.fromAddress if txn_type == TxnType.CREDIT else txn.to
            # )
            # other_user_walletasset = (
            #     await self.walletService.get_walletasset_by_query(
            #         {
            #             "$or": [
            #                 {"address.main": other_user_address},
            #                 {"address.test": other_user_address},
            #             ],
            #             "isDeleted": False,
            #         }
            #     )
            #     if other_user_address
            #     else None
            # )

            tokenasset = await ModelUtilityService.find_one(
                TokenAsset,
                {
                    "network": chain_network.id,
                    "isDeleted": False,
                },
            )
            chain_txn = BlockchainTransaction(
                transactionHash=txn.hash,
                fromAddress=cast(str, txn.fromAddress),
                toAddress=cast(str, txn.to or txn.contractAddress),
                gasPrice=cast(int, txn.gasPrice),
                blockNumber=txn.blockNumber or 0,
                gasUsed=cast(int, txn.gasUsed),
                blockConfirmations=int(txn.confirmations or 0),
                network=cast(PyObjectId, chain_network.id),
                wallet=cast(PyObjectId, wallet.id),
                amount=float(Web3.from_wei(int(txn.value or 0), "ether")),
                status=(
                    TxnStatus.FAILED if (txn.isError == "1") else TxnStatus.SUCCESS
                ),
                isContractExecution=txn.contractAddress != "",
                tokenasset=tokenasset.id if tokenasset else None,
                txnType=txn_type,
                user=cast(PyObjectId, user.id),
                explorerUrl=str(chain_network.blockExplorerUrl) + txn.hash,
                # otherUser=other_user_walletasset.user
                # if other_user_walletasset
                # else None,
                transactedAt=pendulum.from_timestamp(int(txn.timeStamp)),
                source=TxnSource.EXPLORER,
                metaData=txn.dict(by_alias=True),
            ).dict(by_alias=True, exclude_none=True)

            txn_obj.append(chain_txn)

        return txn_obj

    async def swap_between_wraps(
        self,
        value: float,
        mnemonic: str,
        token_asset: TokenAsset,
    ) -> str:
        raise NotImplementedError
