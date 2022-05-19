# -*- coding: utf-8 -*-

from fastapi import Response, status
from fastapi.routing import APIRouter

from apps.appclient.services.appclient_service import AppClientService
from apps.notification.telegram.services.telegram_service import TelegramService
from core.utils.response_service import ResponseService

router = APIRouter(prefix="/api/v1/health-check", tags=["Health Check 🩺"])


appClientService = AppClientService()
telegramService = TelegramService()
responseService = ResponseService()

client_auth = appClientService.client_auth


@router.get("")
def health_check(res: Response):
    return responseService.send_response(
        res, status.HTTP_200_OK, "all good here, works"
    )
