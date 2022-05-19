import abc


class IBlockchainService(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "create_address")
            and callable(subclass.load_data_source)
            or NotImplemented
        )

    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def create_address(self, mnemonic: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def send(self, from_address: str, to: str, value: int) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def get_balance(self, address: str) -> str:
        raise NotImplementedError
