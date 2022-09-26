from typing import Any
from apps.auth.interfaces.auth_interface import AuthResponse
from apps.cloudplatform.interfaces.cloud_interface import CloudProvider, IDType
from apps.cloudplatform.services.cloud_registry import CloudPlatformRegistry
from apps.cloudplatform.interfaces.cloud_interface import UploadFileDTO


class CloudService:
    cloudPlatformRegistry = CloudPlatformRegistry()

    def upload_to_cloud(self, payload: UploadFileDTO) -> str:
        cloud_service = self.cloudPlatformRegistry.get_service(payload.cloudProvider)

        return cloud_service.upload_file(
            payload.authToken, payload.fileName, payload.data
        )

    async def oauth_signin(
        self, cloud_provider: CloudProvider, auth_token: str, token_type: IDType
    ) -> AuthResponse:
        cloud_service = self.cloudPlatformRegistry.get_service(cloud_provider)

        return await cloud_service.oauth_sign_in(auth_token, token_type)

    def recover_file_from_cloud(self, payload: UploadFileDTO) -> Any:
        cloud_service = self.cloudPlatformRegistry.get_service(payload.cloudProvider)

        return cloud_service.recover_file(
            payload.authToken,
            payload.fileName,
        )
