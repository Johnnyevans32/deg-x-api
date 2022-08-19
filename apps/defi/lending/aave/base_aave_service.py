from typing import Any, cast

import eth_utils
from eth_typing import Address
from web3 import Web3
from web3.contract import Contract
from web3.types import Wei

from apps.blockchain.evm_chains.ethereum_service import EthereumService
from apps.blockchain.interfaces.network_interface import Network
from apps.defi.interfaces.defi_provider_interface import DefiProvider
from apps.defi.lending.aave.aave_interface import IReserveTokens, IUserAcccountData
from apps.defi.lending.interfaces.lending_request_interface import InterestRateMode
from apps.defi.lending.services.lending_service_interface import ILendingService
from core.utils.utils_service import Utils, timed_cache


class BaseAaveService(ILendingService):
    ethereumService = EthereumService()
    aave_interest_rate_mode = {
        InterestRateMode.STABLE: 0,
        InterestRateMode.VARIABLE: 1,
    }

    def __init__(self, service_name: str) -> None:
        self.service_name = service_name

    def name(self) -> str:
        return self.service_name

    @staticmethod
    async def get_contract_obj(
        defi_provider: DefiProvider,
        addr: str = None,
        crt_name: str = "ILendingPool",
    ) -> tuple[Contract, Web3]:
        print("get_shwtift")
        str_address = addr if addr else defi_provider.contractAddress
        address = eth_utils.to_bytes(hexstr=str_address)
        network = cast(Network, defi_provider.network)
        web3 = await EthereumService.get_network_provider(network)
        abi = Utils.get_compiled_sol(crt_name, "0.6.12")
        aave_protocol = web3.eth.contract(address=Address(address), abi=abi)
        return aave_protocol, web3

    async def get_user_account_data(
        self, user_addr: str, defi_provider: DefiProvider
    ) -> IUserAcccountData:
        (aave_contract, _) = await BaseAaveService.get_contract_obj(defi_provider)
        user_account_data: list[float] = aave_contract.functions.getUserAccountData(
            eth_utils.to_bytes(hexstr=user_addr)
        ).call()
        (
            total_collateral_eth,
            total_debt_eth,
            available_borrows_eth,
            current_liquidation_threshold,
            ltv,
            health_factory,
        ) = user_account_data

        return IUserAcccountData(
            **{
                "totalCollateralETH": total_collateral_eth,
                "totalDebtETH": total_debt_eth,
                "availableBorrowsETH": available_borrows_eth,
                "currentLiquidationThreshold": current_liquidation_threshold,
                "ltv": ltv,
                "healthFactory": health_factory,
            }
        )

    async def get_user_config(self, user_addr: str, defi_provider: DefiProvider):
        (aave_contract, _) = await BaseAaveService.get_contract_obj(defi_provider)
        user_config_data = aave_contract.functions.getUserConfiguration(
            eth_utils.to_bytes(hexstr=user_addr)
        ).call()
        return user_config_data

    async def deposit(
        self,
        asset: str,
        amount: float,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        referral_code=0,
        gas=80000,
        gas_price=50,
    ):
        try:
            (aave_contract, web3) = await BaseAaveService.get_contract_obj(
                defi_provider
            )
            await self.ethereumService.approve_erc_20_txns(
                asset,
                web3,
                defi_provider.contractAddress,
                amount,
                mnemonic,
            )

            nonce = web3.eth.get_transaction_count(on_behalf_of)
            txn_miner_tip = Wei(web3.eth.max_priority_fee + Web3.toWei(10, "gwei"))
            block_base_fee_per_gas = web3.eth.get_block("latest")["baseFeePerGas"]

            deposit_txn_build = aave_contract.functions.deposit(
                eth_utils.to_bytes(hexstr=asset),
                Web3.toWei(amount, "ether"),
                eth_utils.to_bytes(hexstr=on_behalf_of),
                referral_code,
            ).build_transaction(
                {
                    "nonce": nonce,
                    "gas": Wei(400000),
                    "chainId": web3.eth.chain_id,
                    "maxPriorityFeePerGas": txn_miner_tip,
                    "maxFeePerGas": Wei(block_base_fee_per_gas + txn_miner_tip),
                }
            )

            txn_hash = await self.ethereumService.sign_txn(
                web3, mnemonic, deposit_txn_build
            )
            return txn_hash
        except ValueError as val_err:
            return Utils.get_evm_reverted_reason(val_err.args[0])
        except Exception as err:
            return str(err)

    async def withdraw(
        self,
        asset: str,
        amount: int,
        to: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        gas=70000,
        gas_price=50,
    ) -> Any:
        try:
            (aave_contract, web3) = await BaseAaveService.get_contract_obj(
                defi_provider
            )
            nonce = web3.eth.get_transaction_count(to)
            txn_miner_tip = Wei(web3.eth.max_priority_fee + Web3.toWei(10, "gwei"))
            block_base_fee_per_gas = web3.eth.get_block("latest")["baseFeePerGas"]

            withdraw_txn_build = aave_contract.functions.withdraw(
                eth_utils.to_bytes(hexstr=asset),
                Web3.toWei(amount, "ether"),
                eth_utils.to_bytes(hexstr=to),
            ).build_transaction(
                {
                    "nonce": nonce,
                    "gas": Wei(400000),
                    "chainId": web3.eth.chain_id,
                    "maxPriorityFeePerGas": txn_miner_tip,
                    "maxFeePerGas": Wei(block_base_fee_per_gas + txn_miner_tip),
                }
            )

            txn_hash = await self.ethereumService.sign_txn(
                web3, mnemonic, withdraw_txn_build
            )
            return txn_hash
        except ValueError as val_err:
            return Utils.get_evm_reverted_reason(val_err.args[0])
        except Exception as err:
            return str(err)

    async def borrow(
        self,
        asset: str,
        amount: float,
        interest_rate_mode: InterestRateMode,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        referral_code=0,
        gas=70000,
        gas_price=50,
    ):
        try:
            (aave_contract, web3) = await BaseAaveService.get_contract_obj(
                defi_provider
            )
            nonce = web3.eth.get_transaction_count(on_behalf_of)
            txn_miner_tip = Wei(web3.eth.max_priority_fee + Web3.toWei(10, "gwei"))
            block_base_fee_per_gas = web3.eth.get_block("latest")["baseFeePerGas"]
            borrow_txn_build = aave_contract.functions.borrow(
                eth_utils.to_bytes(hexstr=asset),
                Web3.toWei(amount, "ether"),
                self.aave_interest_rate_mode[interest_rate_mode],
                referral_code,
                eth_utils.to_bytes(hexstr=on_behalf_of),
            ).build_transaction(
                {
                    "nonce": nonce,
                    "gas": Wei(400000),
                    "chainId": web3.eth.chain_id,
                    "maxPriorityFeePerGas": txn_miner_tip,
                    "maxFeePerGas": Wei(block_base_fee_per_gas + txn_miner_tip),
                }
            )
            txn_hash = await self.ethereumService.sign_txn(
                web3, mnemonic, borrow_txn_build
            )
            return txn_hash
        except ValueError as val_err:
            return Utils.get_evm_reverted_reason(val_err.args[0])
        except Exception as err:
            return str(err)

    async def repay(
        self,
        asset: str,
        amount: float,
        rate_mode: InterestRateMode,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        gas=40000,
        gas_price=50,
    ) -> Any:

        try:
            (aave_contract, web3) = await BaseAaveService.get_contract_obj(
                defi_provider
            )
            nonce = web3.eth.get_transaction_count(on_behalf_of)
            txn_miner_tip = Wei(web3.eth.max_priority_fee + Web3.toWei(10, "gwei"))
            block_base_fee_per_gas = web3.eth.get_block("latest")["baseFeePerGas"]

            repay_txn_build = aave_contract.functions.repay(
                eth_utils.to_bytes(hexstr=asset),
                Web3.toWei(amount, "ether"),
                self.aave_interest_rate_mode[rate_mode],
                eth_utils.to_bytes(hexstr=on_behalf_of),
            ).build_transaction(
                {
                    "nonce": nonce,
                    "gas": Wei(400000),
                    "chainId": web3.eth.chain_id,
                    "maxPriorityFeePerGas": txn_miner_tip,
                    "maxFeePerGas": Wei(block_base_fee_per_gas + txn_miner_tip),
                }
            )
            txn_hash = await self.ethereumService.sign_txn(
                web3, mnemonic, repay_txn_build
            )
            return txn_hash
        except ValueError as val_err:
            return Utils.get_evm_reverted_reason(val_err.args[0])
        except Exception as err:
            return str(err)

    async def swap_borrow_rate_mode(
        self,
        asset: str,
        rate_mode: int,
        defi_provider: DefiProvider,
    ):
        (aave_contract, _) = await BaseAaveService.get_contract_obj(defi_provider)
        return aave_contract.functions.swapBorrowRateMode(
            eth_utils.to_bytes(hexstr=asset), rate_mode
        ).call()

    async def set_user_use_reserve_as_collateral(
        self,
        asset: str,
        use_as_collateral: bool,
        defi_provider: DefiProvider,
    ):
        (aave_contract, _) = await BaseAaveService.get_contract_obj(defi_provider)
        return aave_contract.functions.setUserUseReserveAsCollateral(
            eth_utils.to_bytes(hexstr=asset), use_as_collateral
        ).call()

    @timed_cache(10, 10, asyncFunction=True)
    async def get_reserve_assets(
        self, defi_provider: DefiProvider
    ) -> list[IReserveTokens]:
        meta: Any = defi_provider.meta
        print("get_shwtiftsssss")
        (aave_contract, _) = await BaseAaveService.get_contract_obj(
            defi_provider,
            meta["ProtocolDataProvider"]["address"],
            "IProtocolDataProvider",
        )
        reserve_tokens = list(
            map(
                lambda token: IReserveTokens(
                    **{"tokenSymbol": token[0], "tokenAddress": token[1]}
                ),
                aave_contract.functions.getAllReservesTokens().call(),
            )
        )
        return reserve_tokens
