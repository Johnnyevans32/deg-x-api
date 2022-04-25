import random

import sentry_sdk


def traces_sampler(sampling_context):
    print("okk")
    return random.randint(0, 1)
    # return a number between 0 and 1 or a boolean


def sentry_setup() -> None:
    sentry_sdk.init(
        dsn="https://108b246b27ce4bdb9499f17a660a3647@o1049811.ingest.sentry.io/6031090",
        # To set a uniform sample rate
        traces_sample_rate=0.2,
        # Alternatively, to control sampling dynamically
        traces_sampler=traces_sampler,
    )
