import abc
from typing import Any
from apps.auth.interfaces.auth_interface import AuthResponse
from apps.cloudplatform.interfaces.cloud_interface import CloudProvider


class ICloudService(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: Any) -> Any:
        return (
            hasattr(subclass, "oauth_sign_in")
            and callable(subclass.load_data_source)
            or NotImplemented
        )

    @abc.abstractmethod
    def name(self) -> CloudProvider:
        raise NotImplementedError

    @abc.abstractmethod
    async def oauth_sign_in(self, auth_token: str) -> AuthResponse:
        raise NotImplementedError

    @abc.abstractmethod
    def upload_file(self, auth_token: str, file_name: str, data: Any) -> str:
        raise NotImplementedError
