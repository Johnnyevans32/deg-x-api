from typing import Any

from fastapi import status

from apps.featureconfig.interfaces.featureconfig_interface import (
    FeatureConfig,
    FeatureName,
    FeatureStatusUpdateDTO,
)
from apps.notification.slack.services.slack_service import SlackService
from core.db import db
from core.utils.custom_exceptions import UnicornException
from core.utils.model_utility_service import ModelUtilityService


class FeatureConfigService:
    slackService = SlackService()

    def get_feature_by_name(self, name: FeatureName) -> FeatureConfig:
        feature_config = db.featureconfig.find_one({"name": name})

        if feature_config is None:
            feature_config = ModelUtilityService.model_create(
                FeatureConfig,
                FeatureConfig(**{"name": name, "isEnabled": False}).dict(
                    by_alias=True, exclude_none=True
                ),
            )
        else:
            feature_config = FeatureConfig(**feature_config)
        return feature_config

    def is_feature_enabled(self, name: FeatureName) -> bool:
        feature_config = self.get_feature_by_name(name)
        return feature_config.isEnabled and not feature_config.isDeleted

    def check_feature_enabled_or_fail(self, name: FeatureName) -> Any:
        feature_enabled = self.is_feature_enabled(name)
        if not feature_enabled:
            raise UnicornException(
                status_code=status.HTTP_403_FORBIDDEN,
                message=f"{name} has been temporarily disabled",
            )

    def update_feature(
        self,
        feature_name: FeatureName,
        feature_status_update_dto: FeatureStatusUpdateDTO,
    ) -> None:

        query = {"name": feature_name, "isDeleted": False}
        record_to_update = {"isEnabled": feature_status_update_dto.status}

        ModelUtilityService.model_update(FeatureConfig, query, record_to_update)
        self.slackService.send_message(
            f"{feature_name} feature status has been updated to "
            f"{feature_status_update_dto.status}",
            "backend",
        )
