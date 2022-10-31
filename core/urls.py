# -*- coding: utf-8 -*-
from fastapi_restful.inferring_router import InferringRouter

from apps.appclient.controllers.appclient_controller import router as router_client
from apps.auth.controllers.auth_controller import router as router_auth
from apps.auditlog.controllers.auditlog_controller import router as router_audit
from apps.blockchain.controllers.blockchain_controller import (
    router as router_blockchain,
)
from apps.defi.controllers.defi_controller import router as router_defi
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
from apps.cloudplatform.controllers.cloud_controller import router as router_cloud
from apps.user.controllers.user_controller import router as router_user
from apps.networkfee.controllers.networkfee_controller import (
    router as router_networkfee,
)
from apps.marketdata.controllers.marketdata_controller import (
    router as router_marketdata,
)


router = InferringRouter()
router.include_router(router_health_check)
router.include_router(router_auth)
router.include_router(router_wallet)
router.include_router(router_feature)
router.include_router(router_webhook)
router.include_router(router_client)
router.include_router(router_defi_lending)
router.include_router(router_blockchain)
router.include_router(router_defi)
router.include_router(router_cloud)
router.include_router(router_user)
router.include_router(router_audit)
router.include_router(router_networkfee)
router.include_router(router_marketdata)
