from typing import Any
from apps.auth.interfaces.auth_interface import AuthResponse
from apps.cloudplatform.interfaces.cloud_interface import (
    BackupSeedPhraseDTO,
    CloudProvider,
    IDType,
)
from apps.cloudplatform.services.cloud_registry import CloudPlatformRegistry
from apps.user.interfaces.user_interface import User
from core.utils.aes import AesEncryptionService


class CloudService:
    aesEncryptionService = AesEncryptionService()
    cloudPlatformRegistry = CloudPlatformRegistry()

    async def backup_seedphrase(self, payload: BackupSeedPhraseDTO, user: User) -> str:
        assert payload.seed, "no seed phrase found"
        cloud_service = self.cloudPlatformRegistry.get_service(payload.cloudProvider)
        upload_data = (
            await self.aesEncryptionService.encrypt_mnemonic(
                str(user.id), payload.seed, payload.password
            )
        ).dict()
        return cloud_service.upload_file(
            payload.authToken, payload.fileName, upload_data
        )

    async def oauth_signin(
        self, cloud_provider: CloudProvider, auth_token: str, token_type: IDType
    ) -> AuthResponse:
        cloud_service = self.cloudPlatformRegistry.get_service(cloud_provider)

        return await cloud_service.oauth_sign_in(auth_token, token_type)

    def recover_seedphrase(self, payload: BackupSeedPhraseDTO) -> Any:
        cloud_service = self.cloudPlatformRegistry.get_service(payload.cloudProvider)

        return cloud_service.recover_file(
            payload.authToken,
            payload.fileName,
        )
