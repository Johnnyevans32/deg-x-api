# -*- coding: utf-8 -*-
from typing import Sequence
from pydantic import BaseModel
from fastapi import Response, status, APIRouter
from fastapi_restful.cbv import cbv

from apps.auth.services.auth_bearer import CurrentUser
from apps.auditlog.interfaces.notification_interface import NotificationOut
from apps.auditlog.services.auditlog_service import AuditLogService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseModel, ResponseService

router = APIRouter(prefix="/auditlog", tags=["User Notifications 🇳🇬"])


class CreateGenericNotificationDTO(BaseModel):
    title: str
    message: str


@cbv(router)
class AuditLogController:
    auditLogService = AuditLogService()
    responseService = ResponseService()

    @router.get(
        "/notification",
        response_model_by_alias=False,
    )
    async def get_user_transactions(
        self,
        request: UnicornRequest,
        response: Response,
        user: CurrentUser,
        page_num: int = 1,
        page_size: int = 10,
    ) -> ResponseModel[Sequence[NotificationOut]]:
        try:
            request.app.logger.info("getting user notifications")
            res, meta = await self.auditLogService.get_users_notification(
                user, page_num, page_size
            )
            request.app.logger.info("done getting user notifications")
            return self.responseService.send_response(
                response, status.HTTP_200_OK, "user notifications retrieved", res, meta
            )
        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in getting user notifications: {str(e)}",
            )

    @router.post(
        "/notification",
        response_model_by_alias=False,
    )
    async def create_generic_notification(
        self,
        request: UnicornRequest,
        response: Response,
        payload: CreateGenericNotificationDTO,
    ) -> ResponseModel[NotificationOut]:
        try:
            request.app.logger.info("creating user notification")
            res = await self.auditLogService.create_notification(
                payload.title, payload.message
            )
            request.app.logger.info("created user notification")
            return self.responseService.send_response(
                response, status.HTTP_200_OK, "user notification created", res
            )
        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in creating user notification: {str(e)}",
            )
