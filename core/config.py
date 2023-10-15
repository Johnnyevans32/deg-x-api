import os
from functools import lru_cache
from typing import Any
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ~~~~~ APP ~~~~~
    PROJECT_NAME: str = "X"
    PROJECT_DESCRIPTION: str = "X's origin is unknown!!!"
    PROJECT_VERSION: str = "1.0.0"

    # ~~~~~ PATH ~~~~~
    BASE_DIR: Any = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # ~~~~~ TEST ~~~~~
    TEST_RUN: bool = False

    SECRET_KEY: str = os.urandom(32).hex()

    # ~~~~~ CORS ~~~~~
    BACKEND_CORS_ORIGINS: str = "http://localhost:4200"
    # a string of origins separated by commas, e.g: 'http://localhost,
    # http://localhost:4200, http://localhost:3000

    # ~~~~~ EMAIL ~~~~~
    EMAILS_FROM_NAME: str = "Deg X"
    EMAIL_TEMPLATES_DIR: str = "./apps/notification/email/templates/build"
    EMAILS_ENABLED: bool = True
    SLACKING_ENABLED: bool = True

    MAIL_USERNAME: str = "test"
    MAIL_PASSWORD: str = "test"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "test"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    MAIL_SENDER: str = "test"

    # ~~~~~ DATA_BASE ~~~~~
    DATABASE_URI: str = "mongodb://127.0.0.1:27017/"
    DATABASE_NAME: str = "deg-x"

    ACCESS_TOKEN_JWT_SECRET: str = "access"
    ACCESS_TOKEN_EXPIRATION: int = 600  # in MINS

    REFRESH_TOKEN_JWT_SECRET: str = "refresh"
    REFRESH_TOKEN_EXPIRATION: int = 14400

    SERIALIZER_TOKEN_EXPIRATION_IN_SEC: int = 3600

    UI_URL: str = "https://degx.com"

    BASE_URL: str = ""

    # ~~~~~ AWS S3 ~~~~~
    S3_BUCKET_NAME: str = "demo-bucket"
    AWS_ACCESS_KEY_ID: str = "your-access-key-id"
    AWS_SECRET_ACCESS_KEY: str = "your-access-key-secret"
    AWS_S3_URL: str = "http://localhost:4572"

    # ~~~~~ ENVIRONMENT MODE ~~~~~
    ENV_MODE: str = "development"
    SHOW_DOCS_ENVIRONMENT: list[str] = ["local", "staging", "development"]
    IS_DEV: bool = ENV_MODE in SHOW_DOCS_ENVIRONMENT

    # ~~~~~ token generation salt key ~~~~~
    SECURITY_PASSWORD_SALT: str = "my_precious_two"

    # ~~~~~ Loggly ~~~~~
    LOGGLY_HOOK: str = "test"

    # ~~~~~ Slack ~~~~~
    SLACK_HOOK: str = (
        "https://hooks.slack.com/services/"
        "T01T4R47JSH/B01U76TRXJT/DyQJ57eLijWPMlAdp7XC97TU"
    )

    # ~~~~~ Cron ~~~~~
    CRON_ENABLED: bool = True

    # ~~~ Google oauth ~~~~
    WEB_GOOGLE_CLIENT_ID: str = (
        "211971759182-cmu5id6tmr9nk5hq29u7eri7ctdicsja.apps.googleusercontent.com"
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
