# -*- coding: utf-8 -*-
# import json
# from types import SimpleNamespace
# from typing import Any

from fastapi import Response, status
from fastapi.routing import APIRouter

from core.utils.response_service import ResponseService

router = APIRouter(prefix="/api/v1/webhook", tags=["Webhook 🐞"])


responseService = ResponseService()


@router.post("/sentry")
def sentry_webhook(res: Response):
    # payload = json.loads(
    #     sentry_payload.json(), object_hook=lambda d: SimpleNamespace(**d)
    # )
    return responseService.send_response(res, status.HTTP_200_OK, "all good here")
