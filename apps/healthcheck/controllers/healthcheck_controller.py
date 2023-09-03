# -*- coding: utf-8 -*-
from fastapi import Response, status
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from core.utils.response_service import ResponseModel, ResponseService
from core.utils.utils_service import Utils

router = InferringRouter(prefix="/health-check", tags=["Health Check 🩺"])


@cbv(router)
class HealthController:
    responseService = ResponseService()

    @router.get("/")
    def health_check(self, res: Response) -> ResponseModel[None]:
        Utils.create_qr_image()
        return self.responseService.send_response(
            res, status.HTTP_200_OK, "all good here, works"
        )
