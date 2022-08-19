# from typing import Any, cast
# import pendulum

# from apps.blockchain.interfaces.network_interface import Network
# from apps.blockchain.solana.solana_service import SolanaService
# from apps.blockchain.tezos.tezos_service import TezosService
# from apps.defi.interfaces.defi_provider_interface import DefiProvider
# from apps.defi.lending.aave.aave_interface import IReserveTokens, IUserAcccountData
# from apps.defi.lending.interfaces.lending_request_interface import InterestRateMode

# from apps.defi.lending.services.lending_service_interface import ILendingService
# from core.utils.request import HTTPRepository
# from core.utils.utils_service import timed_cache


# from pytezos import pytezos
# from pytezos.client import PyTezosClient


# class YupanaService(ILendingService):
#     solanaService = SolanaService()
#     httpRepository = HTTPRepository()

#     def name(self) -> str:
#         return "yupana_service"

#     async def get_user_account_data(
#         self, user_addr: str, defi_provider: DefiProvider
#     ) -> IUserAcccountData:
#         pass

#     async def get_user_config(self, user_addr: str, defi_provider: DefiProvider):
#         pass

#     async def deposit(
#         self,
#         asset: str,
#         value: float,
#         on_behalf_of: str,
#         defi_provider: DefiProvider,
#         mnemonic: str,
#         referral_code=0,
#         gas=80000,
#         gas_price=50,
#     ):
#         key = TezosService.get_key_from_mnemonic(mnemonic)
#         network = cast(Network, defi_provider.network)
#         tez_client: PyTezosClient = pytezos.using(network.providerUrl, key)
#         crt = tez_client.contract(defi_provider.contractAddress)
#         amount = int(self.solanaService.format_num(value, "to"))
#         deposit_op = crt.accrueInterest(tokenId=1, amount=amount).operation_group
#         print("deposit_op", deposit_op)
#         res = deposit_op.fill().sign().inject()
#         return res

#     async def withdraw(
#         self,
#         asset: str,
#         value: int,
#         to: str,
#         defi_provider: DefiProvider,
#         mnemonic: str,
#         gas=70000,
#         gas_price=50,
#     ) -> Any:
#         key = TezosService.get_key_from_mnemonic(mnemonic)
#         network = cast(Network, defi_provider.network)
#         tez_client: PyTezosClient = pytezos.using(network.providerUrl, key)
#         crt = tez_client.contract(defi_provider.contractAddress)
#         amount = int(self.solanaService.format_num(value, "to"))
#         withdraw_op = crt.withdrawReserve(tokenId=1, amount=amount).operation_group
#         print(withdraw_op)
#         res = withdraw_op.fill().sign().inject()
#         return res

#     async def borrow(
#         self,
#         asset: str,
#         value: float,
#         interest_rate_mode: InterestRateMode,
#         on_behalf_of: str,
#         defi_provider: DefiProvider,
#         mnemonic: str,
#         referral_code=0,
#         gas=70000,
#         gas_price=50,
#     ):
#         key = TezosService.get_key_from_mnemonic(mnemonic)
#         network = cast(Network, defi_provider.network)
#         tez_client: PyTezosClient = pytezos.using(network.providerUrl, key)
#         crt = tez_client.contract(defi_provider.contractAddress)
#         amount = int(self.solanaService.format_num(value, "to"))
#         borrow_op = crt.borrow(
#             tokenId=1, amount=amount, deadline=pendulum.now().int_timestamp
#         ).operation_group
#         print(borrow_op)
#         res = borrow_op.fill().sign().inject()
#         return res

#     async def repay(
#         self,
#         asset: str,
#         value: float,
#         rate_mode: InterestRateMode,
#         on_behalf_of: str,
#         defi_provider: DefiProvider,
#         mnemonic: str,
#         gas=40000,
#         gas_price=50,
#     ) -> Any:
#         key = TezosService.get_key_from_mnemonic(mnemonic)
#         network = cast(Network, defi_provider.network)
#         tez_client: PyTezosClient = pytezos.using(network.providerUrl, key)
#         crt = tez_client.contract(defi_provider.contractAddress)
#         amount = int(self.solanaService.format_num(value, "to"))
#         repay_op = crt.repay(
#             tokenId=1, amount=amount, deadline=pendulum.now().int_timestamp
#         ).operation_group
#         print(repay_op)
#         res = repay_op.fill().sign().inject()
#         return res

#     async def swap_borrow_rate_mode(
#         self,
#         asset: str,
#         rate_mode: int,
#         defi_provider: DefiProvider,
#     ):
#         pass

#     async def set_user_use_reserve_as_collateral(
#         self,
#         asset: str,
#         use_as_collateral: bool,
#         defi_provider: DefiProvider,
#     ):
#         pass

#     @timed_cache(10, 10, asyncFunction=True)
#     async def get_reserve_assets(
#         self, defi_provider: DefiProvider
#     ) -> list[IReserveTokens]:
#         pass
