import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Config:
    TEST = {
        "database": "test_default",
    }


# ~~~~~ SECRET ~~~~~
SECRET_KEY = os.getenv("SECRET_KEY", "cuerno de unicornio :D")


def getenv_boolean(var_name, default_value=False):
    result = default_value
    env_value = os.getenv(var_name)
    if env_value is not None:
        result = env_value.upper() in ("TRUE", "1")
    return result


class Settings(BaseSettings):
    # ~~~~~ APP ~~~~~
    PROJECT_NAME = os.getenv("PROJECT_NAME", "Boiler Plate")
    PROJECT_DESCRIPTION = os.getenv("PROJECT_DESCRIPTION", "Boiler Plate")

    # ~~~~~ PATH ~~~~~
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # ~~~~~ TEST ~~~~~
    TEST_RUN = getenv_boolean("TEST_RUN", False)

    if not SECRET_KEY:
        SECRET_KEY = os.urandom(32)

    # ~~~~~ APPS ~~~~~
    APPS = [
        "healthcheck",
        "user",
    ]

    # ~~~~~ CORS ~~~~~
    BACKEND_CORS_ORIGINS = os.getenv(
        "BACKEND_CORS_ORIGINS", "http://localhost:4200"
    )  # a string of origins separated by commas, e.g: 'http://localhost,
    # http://localhost:4200, http://localhost:3000

    # ~~~~~ EMAIL ~~~~~
    # SENTRY_DSN = os.getenv('SENTRY_DSN')

    EMAILS_FROM_NAME = PROJECT_NAME
    EMAIL_TEMPLATES_DIR = "./apps/notification/email/templates/build"
    EMAILS_ENABLED = getenv_boolean("EMAILS_ENABLED", True)

    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "test")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "test")
    MAIL_PORT = os.getenv("MAIL_PORT", "test")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "test")
    MAIL_TLS = getenv_boolean("MAIL_TLS")
    MAIL_SSL = getenv_boolean("MAIL_SSL")
    MAIL_SENDER = os.getenv("MAIL_SENDER", "test")

    # ~~~~~ DATA_BASE ~~~~~
    DATABASE_URI = os.getenv("DATABASE_URI", "mongodb://127.0.0.1:27017/")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "deg-x")
    DATABASE = {"NAME": DATABASE_NAME, "URI": DATABASE_URI}

    ACCESS_TOKEN_JWT_SECRET = os.getenv("ACCESS_TOKEN_JWT_SECRET", "accesssecret")
    ACCESS_TOKEN_EXPIRATION = int(os.getenv("ACCESS_TOKEN_EXPIRATION", 10))

    REFRESH_TOKEN_JWT_SECRET = os.getenv("REFRESH_TOKEN_JWT_SECRET", "refreshsecret")
    REFRESH_TOKEN_EXPIRATION = int(os.getenv("REFRESH_TOKEN_EXPIRATION", 14400))

    SERIALIZER_TOKEN_EXPIRATION_IN_SEC = int(os.getenv("TOKEN_EXPIRATION_IN_SEC", 3600))

    UI_URL = "https://simthrift.net/"

    # ~~~~~ AWS S3 ~~~~~
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "demo-bucket")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "your-access-key-id")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "your-access-key-secret")
    AWS_S3_URL = os.getenv("AWS_S3_URL", "http://localhost:4572")

    # ~~~~~ ENVIRONMENT MODE ~~~~~
    ENV_MODE = os.getenv("ENV_MODE", "development")
    IS_DEV = ENV_MODE == "development"

    # ~~~~~ token generation salt key ~~~~~
    SECURITY_PASSWORD_SALT = "my_precious_two"

    # ~~~~~ Loggly ~~~~~
    LOGGLY_HOOK = os.getenv("LOGGLY_HOOK", "test")

    # ~~~~~ Slack ~~~~~
    SLACK_HOOK = os.getenv(
        "SLACK_HOOK",
        "https://hooks.slack.com/services/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",
    )

    # ~~~~~ Cron ~~~~~
    CRON_ENABLED = getenv_boolean("CRON_ENABLED", True)

    # ~~~ Google oauth ~~~~
    GOOGLE_CLIENT_ID = os.getenv(
        "GOOGLE_CLIENT_ID",
        "211971759182-bvjf8k5etbn2cj9hitmfi315aaurur6i.apps.googleusercontent.com",
    )

    class Config:
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
