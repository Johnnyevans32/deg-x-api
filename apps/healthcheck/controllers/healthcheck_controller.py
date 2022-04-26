# -*- coding: utf-8 -*-

from fastapi.routing import APIRouter

from apps.appclient.services.appclient_service import AppClientService

router = APIRouter(prefix="/api/v1/health-check", tags=["Health Check 🩺"])


appClientService = AppClientService()

client_auth = appClientService.client_auth


@router.get("")
def health_check():
    return "all good here, workkkks"
