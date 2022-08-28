from apps.blockchain.binance.bsc_service import BSCService

# from apps.blockchain.binance.bnb_service import BNBService
from apps.blockchain.bitcoin.bitcoin_service import BitcoinService
from apps.blockchain.bitcoin.dashcoin_service import DashcoinService
from apps.blockchain.bitcoin.dogecoin_service import DogecoinService
from apps.blockchain.bitcoin.litecoin_service import LitecoinService
from apps.blockchain.evm_chains.avax_service import AvaxService
from apps.blockchain.evm_chains.ethereum_service import EthereumService
from apps.blockchain.evm_chains.polygon_service import PolygonService
from apps.blockchain.evm_chains.tron_service import TronService
from apps.blockchain.interfaces.blockchain_interface import ChainServiceName
from apps.blockchain.solana.solana_service import SolanaService
from apps.blockchain.tezos.tezos_service import TezosService
from apps.blockchain.types.blockchain_service_interface import IBlockchainService
from core.utils.loggly import logger


class BlockchainRegistry:
    ethereumService = EthereumService()
    bitcoinService = BitcoinService()
    solanaService = SolanaService()
    tezosService = TezosService()
    dogecoinService = DogecoinService()
    # bnbService = BNBService()
    bscService = BSCService()
    dashService = DashcoinService()
    litecoinService = LitecoinService()
    polygonService = PolygonService()
    avaxService = AvaxService()
    tronService = TronService()

    registry: dict[ChainServiceName, IBlockchainService] = {}

    def __init__(self) -> None:
        self.register_services()

    def set_service(self, key: ChainServiceName, service: IBlockchainService):
        logger.info(f"network chain registed key - {key}")
        self.registry[key] = service

    def register_services(self) -> None:
        logger.info("network chain registering")
        self.set_service(self.ethereumService.name(), self.ethereumService)
        self.set_service(self.bitcoinService.name(), self.bitcoinService)
        self.set_service(self.solanaService.name(), self.solanaService)
        self.set_service(self.tezosService.name(), self.tezosService)
        self.set_service(self.dogecoinService.name(), self.dogecoinService)
        # self.set_service(self.bnbService.name(), self.bnbService)
        self.set_service(self.bscService.name(), self.bscService)
        self.set_service(self.dashService.name(), self.dashService)
        self.set_service(self.litecoinService.name(), self.litecoinService)
        self.set_service(self.polygonService.name(), self.polygonService)
        self.set_service(self.avaxService.name(), self.avaxService)
        self.set_service(self.tronService.name(), self.tronService)

    def get_service(self, key: ChainServiceName) -> IBlockchainService:
        return self.registry[key]
