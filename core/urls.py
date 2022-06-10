# -*- coding: utf-8 -*-

from fastapi.routing import APIRouter

from apps.appclient.controllers.appclient_controller import router as router_client
from apps.auth.controllers.auth_controller import router as router_auth
from apps.blockchain.controllers.blockchain_controller import (
    router as router_blockchain,
)
from apps.defi.lending.controllers.lending_controller import (
    router as router_defi_lending,
)
from apps.featureconfig.controllers.featureconfig_controller import (
    router as router_feature,
)
from apps.healthcheck.controllers.healthcheck_controller import (
    router as router_health_check,
)
from apps.wallet.controllers.wallet_controller import router as router_wallet
from apps.webhook.controllers.webhook_controller import router as router_webhook

router = APIRouter()
# router = InferringRouter()
router.include_router(router_health_check)
router.include_router(router_auth)
router.include_router(router_wallet)
router.include_router(router_feature)
router.include_router(router_webhook)
router.include_router(router_client)
router.include_router(router_defi_lending)
router.include_router(router_blockchain)
