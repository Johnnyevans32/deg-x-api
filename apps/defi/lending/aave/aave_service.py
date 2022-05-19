import eth_utils
from eth_typing import Address
from web3.contract import Contract

from apps.blockchain.ethereum.ethereum_service import EthereumService
from apps.defi.lending.aave.aave_interface import IUserAcccountData
from apps.defi.lending.types.lending_service_interface import ILendingService
from core.config import settings
from core.utils.helper_service import HelperService


class AaveService(ILendingService):
    address: bytes
    ethereumService = EthereumService()

    def __init__(self) -> None:
        super().__init__()
        self.address = eth_utils.to_bytes(hexstr=settings.AAVE_CONTRACT_ADDRESS)

    def name(self) -> str:
        return "aave"

    def get_contract_obj(self) -> Contract:
        web3 = self.ethereumService.get_network_provider()
        abi = HelperService.get_compiled_sol("ILendingPool", "0.6.12")
        aave_protocol = web3.eth.contract(address=Address(self.address), abi=abi)

        return aave_protocol

    def get_user_account_data(self, user: bytes) -> IUserAcccountData:
        aave_contract = self.get_contract_obj()
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

    def get_user_config(self, user: bytes):
        aave_contract = self.get_contract_obj()
        user_config_data = aave_contract.functions.getUserConfiguration(user).call()

        print(user_config_data)
        return user_config_data

    def deposit(self, asset: bytes, amount: int, on_behalf_of: bytes, referral_code=0):
        aave_contract = self.get_contract_obj()
        return aave_contract.functions.deposit(
            asset, amount, on_behalf_of, referral_code
        ).call()

    def withdraw(self, asset: bytes, amount: int, to: bytes) -> float:
        aave_contract = self.get_contract_obj()
        return aave_contract.functions.withdraw(asset, amount, to).call()

    def borrow(
        self,
        asset: bytes,
        amount: int,
        interest_rate_mode: int,
        on_behalf_of: bytes,
        referral_code=0,
    ):
        aave_contract = self.get_contract_obj()
        return aave_contract.functions.borrow(
            asset, amount, interest_rate_mode, referral_code, on_behalf_of
        ).call()

    def repay(
        self,
        asset: bytes,
        amount: int,
        rate_mode: int,
        on_behalf_of: bytes,
    ) -> float:
        aave_contract = self.get_contract_obj()
        return aave_contract.functions.repay(
            asset, amount, rate_mode, on_behalf_of
        ).call()

    def swap_borrow_rate_mode(self, asset: bytes, rateMode: int):
        aave_contract = self.get_contract_obj()
        return aave_contract.functions.swapBorrowRateMode(asset, rateMode).call()

    def set_user_use_reserve_as_collateral(self, asset: bytes, use_as_collateral: bool):
        aave_contract = self.get_contract_obj()
        return aave_contract.functions.setUserUseReserveAsCollateral(
            asset, use_as_collateral
        ).call()
