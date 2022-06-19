import eth_utils
from eth_typing import Address
from web3.contract import Contract

from apps.blockchain.ethereum.ethereum_service import EthereumService
from apps.defi.interfaces.defi_provider_interface import DefiProvider
from apps.defi.lending.aave.aave_interface import IUserAcccountData
from apps.defi.lending.interfaces.lending_request_interface import InterestRateMode
from apps.defi.lending.types.lending_service_interface import ILendingService
from core.utils.utils_service import Utils


class AaveService(ILendingService):
    ethereumService = EthereumService()
    aave_interest_rate_mode = {
        InterestRateMode.STABLE: 0,
        InterestRateMode.VARIABLE: 1,
    }

    def name(self) -> str:
        return "aave_service"

    def get_contract_obj(
        self,
        defi_provider: DefiProvider,
        addr: str = None,
        crt_name: str = "ILendingPool",
    ) -> Contract:
        str_address = defi_provider.contractAddress if addr is None else addr
        address = eth_utils.to_bytes(hexstr=str_address)
        web3 = self.ethereumService.get_network_provider(defi_provider.network)
        abi = Utils.get_compiled_sol(crt_name, "0.6.12")
        aave_protocol = web3.eth.contract(address=Address(address), abi=abi)

        return aave_protocol

    def get_user_account_data(
        self, user: bytes, defi_provider: DefiProvider
    ) -> IUserAcccountData:
        aave_contract = self.get_contract_obj(defi_provider)
        user_account_data: list[float] = aave_contract.functions.getUserAccountData(
            user
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

    def get_user_config(self, user: bytes, defi_provider: DefiProvider):
        aave_contract = self.get_contract_obj(defi_provider)
        user_config_data = aave_contract.functions.getUserConfiguration(user).call()
        return user_config_data

    def deposit(
        self,
        asset: bytes,
        amount: float,
        on_behalf_of: bytes,
        defi_provider: DefiProvider,
        referral_code=0,
    ):
        aave_contract = self.get_contract_obj(defi_provider)
        return aave_contract.functions.deposit(
            asset, amount, on_behalf_of, referral_code
        ).call()

    def withdraw(
        self,
        asset: bytes,
        amount: int,
        to: bytes,
        defi_provider: DefiProvider,
    ) -> float:
        aave_contract = self.get_contract_obj(defi_provider)
        return aave_contract.functions.withdraw(asset, amount, to).call()

    def borrow(
        self,
        asset: bytes,
        amount: float,
        interest_rate_mode: InterestRateMode,
        on_behalf_of: bytes,
        defi_provider: DefiProvider,
        referral_code=0,
    ):
        aave_contract = self.get_contract_obj(defi_provider)
        return aave_contract.functions.borrow(
            asset,
            amount,
            self.aave_interest_rate_mode[interest_rate_mode],
            referral_code,
            on_behalf_of,
        ).call()

    def repay(
        self,
        asset: bytes,
        amount: float,
        rate_mode: InterestRateMode,
        on_behalf_of: bytes,
        defi_provider: DefiProvider,
    ) -> float:
        aave_contract = self.get_contract_obj(defi_provider)
        return aave_contract.functions.repay(
            asset, amount, self.aave_interest_rate_mode[rate_mode], on_behalf_of
        ).call()

    def swap_borrow_rate_mode(
        self,
        asset: bytes,
        rate_mode: int,
        defi_provider: DefiProvider,
    ):
        aave_contract = self.get_contract_obj(defi_provider)
        return aave_contract.functions.swapBorrowRateMode(asset, rate_mode).call()

    def set_user_use_reserve_as_collateral(
        self,
        asset: bytes,
        use_as_collateral: bool,
        defi_provider: DefiProvider,
    ):
        aave_contract = self.get_contract_obj(defi_provider)
        return aave_contract.functions.setUserUseReserveAsCollateral(
            asset, use_as_collateral
        ).call()

    def get_reserved_assets(self, defi_provider: DefiProvider):
        # meta: Any = defi_provider.meta
        aave_contract = self.get_contract_obj(
            defi_provider,
        )
        return aave_contract.functions.getAddressesProvider().call()
