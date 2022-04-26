# -*- coding: utf-8 -*-
from typing import Any

from fastapi import Response, status
from fastapi.routing import APIRouter

from apps.appclient.services.appclient_service import AppClientService
from apps.blockchain.services.blockchain_service import BlockchainService
from apps.wallet.interfaces.wallet_interface import Wallet
from core.utils.model_utility_service import ModelUtilityService
from core.utils.response_service import ResponseService

router = APIRouter(prefix="/api/v1/health-check", tags=["Health Check 🩺"])


appClientService = AppClientService()

client_auth = appClientService.client_auth


@router.get("")
def health_check():

    print(
        ModelUtilityService.populate_and_paginate_data(
            Wallet, {"walletType": "multichain"}, ["ksls", "kjss"]
        )
    )
    # print("response", self.response.__dict__)
    return "all good here, workkkks"
