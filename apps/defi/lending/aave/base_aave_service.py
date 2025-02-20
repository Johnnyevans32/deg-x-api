from typing import Any, cast

from eth_typing import Address, HexStr
from web3 import Web3
from web3.contract.async_contract import AsyncContract

from apps.blockchain.evm_chains.ethereum_service import EthereumService
from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.network_interface import Network
from apps.defi.interfaces.defiprovider_interface import DefiProvider
from apps.defi.lending.types.lending_types import IReserveToken, IUserAcccountData
from apps.defi.lending.interfaces.lending_request_interface import InterestRateMode
from apps.defi.lending.services.lending_iservice import ILendingService
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

    @timed_cache(10000, 10, asyncFunction=True)
    async def get_contract_obj(
        self,
        defi_provider: DefiProvider,
        addr: str | None,
        crt_name: str = "ILendingPool",
    ) -> tuple[AsyncContract, Web3]:
        str_address = addr if addr else defi_provider.contractAddress
        address = Web3.to_bytes(hexstr=HexStr(str_address))
        network = cast(Network, defi_provider.network)
        web3 = self.ethereumService.get_network_provider(network)
        abi = await Utils.get_compiled_sol(crt_name, "0.6.12")
        aave_protocol = cast(
            AsyncContract, web3.eth.contract(address=Address(address), abi=abi)
        )
        return aave_protocol, web3

    async def get_user_account_data(
        self, user_addr: str, defi_provider: DefiProvider
    ) -> IUserAcccountData:
        (aave_contract, _) = await self.get_contract_obj(defi_provider)
        user_account_data: list[float] = aave_contract.functions.getUserAccountData(
            Web3.to_bytes(hexstr=HexStr(user_addr))
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
            totalCollateral=total_collateral_eth,
            totalDebt=total_debt_eth,
            availableBorrows=available_borrows_eth,
            healthFactory=health_factory,
        )

    async def get_user_config(self, user_addr: str, defi_provider: DefiProvider) -> Any:
        (aave_contract, _) = await self.get_contract_obj(defi_provider)
        user_config_data = aave_contract.functions.getUserConfiguration(
            Web3.to_bytes(hexstr=HexStr(user_addr))
        ).call()
        return user_config_data

    async def deposit(
        self,
        asset: str,
        amount: float,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        referral_code: int = 0,
        gas: int = 80000,
        gas_price: int = 50,
    ) -> str:
        try:
            (aave_contract, web3) = await self.get_contract_obj(defi_provider)
            network = cast(Network, defi_provider.network)
            blockchain = cast(Blockchain, defi_provider.blockchain)
            await self.ethereumService.approve_token_delegation(
                network,
                blockchain,
                mnemonic,
                amount,
                asset,
                defi_provider.contractAddress,
            )

            deposit_txn_build = aave_contract.functions.deposit(
                Web3.to_bytes(hexstr=HexStr(asset)),
                Web3.to_wei(amount, "ether"),
                Web3.to_bytes(hexstr=HexStr(on_behalf_of)),
                referral_code,
            ).build_transaction()

            txn_hash = await self.ethereumService.sign_txn(
                network, blockchain, mnemonic, deposit_txn_build
            )
            return txn_hash
        except ValueError as val_err:
            return Utils.get_evm_reverted_reason(val_err.args[0])
        except Exception as err:
            return str(err)

    async def withdraw(
        self,
        asset: str,
        amount: float,
        to: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        gas: int = 70000,
        gas_price: int = 50,
    ) -> str:
        try:
            (aave_contract, web3) = await self.get_contract_obj(defi_provider)
            network = cast(Network, defi_provider.network)
            blockchain = cast(Blockchain, defi_provider.blockchain)
            withdraw_txn_build = aave_contract.functions.withdraw(
                Web3.to_bytes(hexstr=HexStr(asset)),
                Web3.to_wei(amount, "ether"),
                Web3.to_bytes(hexstr=HexStr(to)),
            ).build_transaction()

            txn_hash = await self.ethereumService.sign_txn(
                network, blockchain, mnemonic, withdraw_txn_build
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
        referral_code: int = 0,
        gas: int = 70000,
        gas_price: int = 50,
    ) -> str:
        try:
            (aave_contract, web3) = await self.get_contract_obj(defi_provider)
            network = cast(Network, defi_provider.network)
            blockchain = cast(Blockchain, defi_provider.blockchain)
            borrow_txn_build = aave_contract.functions.borrow(
                Web3.to_bytes(hexstr=HexStr(asset)),
                Web3.to_wei(amount, "ether"),
                self.aave_interest_rate_mode[interest_rate_mode],
                referral_code,
                Web3.to_bytes(hexstr=HexStr(on_behalf_of)),
            ).build_transaction()
            txn_hash = await self.ethereumService.sign_txn(
                network, blockchain, mnemonic, borrow_txn_build
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
        gas: int = 40000,
        gas_price: int = 50,
    ) -> Any:

        try:
            (aave_contract, web3) = await self.get_contract_obj(defi_provider)
            network = cast(Network, defi_provider.network)
            blockchain = cast(Blockchain, defi_provider.blockchain)
            await self.ethereumService.approve_token_delegation(
                network,
                blockchain,
                mnemonic,
                amount,
                asset,
                defi_provider.contractAddress,
            )

            repay_txn_build = aave_contract.functions.repay(
                Web3.to_bytes(hexstr=HexStr(asset)),
                Web3.to_wei(amount, "ether"),
                self.aave_interest_rate_mode[rate_mode],
                Web3.to_bytes(hexstr=HexStr(on_behalf_of)),
            ).build_transaction()
            txn_hash = await self.ethereumService.sign_txn(
                network, blockchain, mnemonic, repay_txn_build
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
    ) -> Any:
        (aave_contract, _) = await self.get_contract_obj(defi_provider)
        return aave_contract.functions.swapBorrowRateMode(
            Web3.to_bytes(hexstr=HexStr(asset)), rate_mode
        ).call()

    async def set_user_use_reserve_as_collateral(
        self,
        asset: str,
        use_as_collateral: bool,
        defi_provider: DefiProvider,
    ) -> Any:
        (aave_contract, _) = await self.get_contract_obj(defi_provider)
        return aave_contract.functions.setUserUseReserveAsCollateral(
            Web3.to_bytes(hexstr=HexStr(asset)), use_as_collateral
        ).call()

    @timed_cache(10, 10, asyncFunction=True)
    async def get_reserve_assets(
        self, defi_provider: DefiProvider
    ) -> list[IReserveToken]:
        meta: Any = defi_provider.meta
        (aave_contract, _) = await self.get_contract_obj(
            defi_provider,
            meta["ProtocolDataProvider"]["address"],
            "IProtocolDataProvider",
        )

        def get_reserve_asset_data(
            symbol: str,
            asset: str,
        ) -> IReserveToken:
            res_data = aave_contract.functions.getReserveData(
                Web3.to_bytes(hexstr=HexStr(asset))
            ).call()
            (
                availableLiquidity,
                totalStableDebt,
                totalVariableDebt,
                liquidityRate,
                variableBorrowRate,
                stableBorrowRate,
                averageStableBorrowRate,
                liquidityIndex,
                variableBorrowIndex,
                lastUpdateTimestamp,
            ) = res_data
            res_config_data = aave_contract.functions.getReserveConfigurationData(
                Web3.to_bytes(hexstr=HexStr(asset))
            ).call()
            (
                decimals,
                ltv,
                liquidationThreshold,
                liquidationBonus,
                reserveFactor,
                usageAsCollateralEnabled,
                borrowingEnabled,
                stableBorrowRateEnabled,
                isActive,
                isFrozen,
            ) = res_config_data

            return IReserveToken(
                tokenSymbol=symbol,
                tokenAddress=asset,
                borrowingEnabled=borrowingEnabled,
                usageAsCollateralEnabled=usageAsCollateralEnabled,
                liquidityRate=liquidityRate / liquidityIndex,
                availableLiquidity=availableLiquidity / 10**decimals,
                variableBorrowRate=variableBorrowRate / variableBorrowIndex,
                stableBorrowRate=stableBorrowRate / variableBorrowIndex,
                ltv=ltv / 100,
            )

        reserve_tokens = list(
            map(
                lambda token: get_reserve_asset_data(token[0], token[1]),
                aave_contract.functions.getAllReservesTokens().call(),
            )
        )
        return reserve_tokens
