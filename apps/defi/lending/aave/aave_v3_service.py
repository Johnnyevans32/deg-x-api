from apps.defi.lending.aave.base_aave_service import BaseAaveService


class AaveV3Service(BaseAaveService):
    def __init__(self) -> None:
        super().__init__("aave_v3_ervice")
