from typing import Any
from fastapi import BackgroundTasks, Response
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter
from starlette import status
from apps.cloudplatform.interfaces.cloud_interface import UploadFileDTO
from apps.cloudplatform.services.cloud_service import CloudService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseModel, ResponseService
from core.middleware.encryption import DecrptRequestRoute

router = InferringRouter(
    prefix="/cloud", tags=["Cloud"], route_class=DecrptRequestRoute
)


@cbv(router)
class CloudController:
    responseService = ResponseService()
    cloudService = CloudService()

    @router.post(
        "/upload-file",
        status_code=status.HTTP_201_CREATED,
    )
    def upload_file_to_cloud(
        self,
        request: UnicornRequest,
        res: Response,
        background_tasks: BackgroundTasks,
        payload: UploadFileDTO,
    ) -> ResponseModel[str]:
        try:
            request.app.logger.info("uploading file to cloud")
            resp = self.cloudService.upload_to_cloud(payload)
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
        "/recover-file",
        status_code=status.HTTP_201_CREATED,
    )
    def recover_file_from_cloud(
        self,
        request: UnicornRequest,
        res: Response,
        background_tasks: BackgroundTasks,
        payload: UploadFileDTO,
    ) -> ResponseModel[Any]:
        try:
            request.app.logger.info("recovering file from cloud")
            resp = self.cloudService.recover_file_from_cloud(payload)
            request.app.logger.info("recovered file to cloud")
            return self.responseService.send_response(
                res, status.HTTP_200_OK, "file recovered successful", resp
            )
        except Exception as e:
            request.app.logger.error(f"Error recovering file from cloud, {str(e)}")
            return self.responseService.send_response(
                res, status.HTTP_400_BAD_REQUEST, f"file recovering failed: {str(e)}"
            )
