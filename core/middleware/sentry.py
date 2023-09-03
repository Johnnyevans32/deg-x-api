import random
from typing import Any, Dict

from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
import sentry_sdk


def traces_sampler(sampling_context: Dict[str, Any]) -> int:
    return random.randint(0, 1)
    # return a number between 0 and 1 or a boolean


def sentry_setup() -> None:
    sentry_sdk.init(
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
        ],
        dsn="https://108b246b27ce4bdb9499f17a660a3647@o1049811.ingest.sentry.io/6031090",
        # To set a uniform sample rate
        traces_sample_rate=0.2,
        # Alternatively, to control sampling dynamically
        traces_sampler=traces_sampler,
        send_default_pii=True,
    )
