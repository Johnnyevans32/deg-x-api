import abc


class IBlockchainService(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "create_account")
            and callable(subclass.load_data_source)
            or NotImplemented
        )

    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def create_address(self, mnemonic: str) -> str:
        raise NotImplementedError
