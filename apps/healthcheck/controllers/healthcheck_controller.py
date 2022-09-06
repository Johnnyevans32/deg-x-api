# -*- coding: utf-8 -*-
from pydantic import BaseModel
from fastapi import Response, status
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter
from core.utils.aes import encrypt_AES_GCM, decrypt_AES_GCM

from core.utils.response_service import ResponseModel, ResponseService

router = InferringRouter(prefix="/health-check", tags=["Health Check 🩺"])


class Name(BaseModel):
    name: str


@cbv(router)
class HealthController:
    responseService = ResponseService()

    @router.get("/")
    def health_check(self, res: Response) -> ResponseModel[None]:
        yh_res = encrypt_AES_GCM("12345", {"name": "evans"}, "password")
        print("yh_res", yh_res)
        de_res = decrypt_AES_GCM(yh_res, Name, "password")
        print("de_res", de_res)
        return self.responseService.send_response(
            res, status.HTTP_200_OK, "all good here, works"
        )
