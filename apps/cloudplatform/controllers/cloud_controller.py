from typing import Any
from fastapi import BackgroundTasks, Response, Depends, APIRouter
from fastapi_restful.cbv import cbv
from starlette import status

from apps.auth.services.auth_bearer import JWTBearer
from apps.cloudplatform.interfaces.cloud_interface import BackupSeedPhraseDTO
from apps.cloudplatform.services.cloud_service import CloudService

from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseModel, ResponseService
from core.middleware.encryption import DecrptRequestRoute

router = APIRouter(prefix="/cloud", tags=["Cloud"], route_class=DecrptRequestRoute)


@cbv(router)
class CloudController:
    responseService = ResponseService()
    cloudService = CloudService()

    @router.post(
        "/backup",
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(JWTBearer())],
    )
    async def backup_mnemonic(
        self,
        request: UnicornRequest,
        res: Response,
        background_tasks: BackgroundTasks,
        payload: BackupSeedPhraseDTO,
    ) -> ResponseModel[str]:
        try:
            user = request.state.user
            request.app.logger.info("uploading file to cloud")
            resp = await self.cloudService.backup_seedphrase(payload, user)
            request.app.logger.info("uploaded file to cloud")
            return self.responseService.send_response(
                res, status.HTTP_200_OK, "file upload successful", resp
            )
        except Exception as e:
            request.app.logger.error(f"Error uploading file to cloud, {str(e)}")
            return self.responseService.send_response(
                res, status.HTTP_400_BAD_REQUEST, f"file upload failed: {str(e)}"
            )

    @router.post(
        "/recovery",
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(JWTBearer())],
    )
    def recover_file_from_cloud(
        self,
        request: UnicornRequest,
        res: Response,
        background_tasks: BackgroundTasks,
        payload: BackupSeedPhraseDTO,
    ) -> ResponseModel[Any]:
        try:
            request.app.logger.info("recovering file from cloud")
            resp = self.cloudService.recover_seedphrase(payload)
            request.app.logger.info("recovered file to cloud")
            return self.responseService.send_response(
                res, status.HTTP_200_OK, "file recovered successful", resp
            )
        except Exception as e:
            request.app.logger.error(f"Error recovering file from cloud, {str(e)}")
            return self.responseService.send_response(
                res, status.HTTP_400_BAD_REQUEST, f"file recovering failed: {str(e)}"
            )
