import os

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    postgres_host: str = Field(os.getenv("POSTGRES_HOST"))
    postgres_user: str = Field(os.getenv("POSTGRES_USER"))
    postgres_password: str = Field(os.getenv("POSTGRES_PASSWORD"))
    postgres_database_name: str = Field(os.getenv("POSTGRES_DB"))

    redis_host: str = Field(os.getenv("REDIS_HOST"))
    redis_port: str = Field(os.getenv("REDIS_PORT"))

    jwt_secret: str = Field(os.getenv("JWT_SECRET_KEY"))
    flask_secret: str = Field(os.getenv("FLASK_SECRET_KEY"))

    yandex_client_id: str = Field(os.getenv("YANDEX_CLIENT_ID"))
    yandex_client_secret: str = Field(os.getenv("YANDEX_CLIENT_SECRET"))

    yandex_authorize_url: str = Field(os.getenv("YANDEX_AUTHORIZE_URL"))
    yandex_access_token_url: str = Field(os.getenv("YANDEX_ACCESS_TOKEN_URL"))
    yandex_userinfo_endpoint: str = Field(os.getenv("YANDEX_USERINFO_ENDPOINT"))

    google_client_id: str = Field(os.getenv("GOOGLE_CLIENT_ID"))
    google_client_secret: str = Field(os.getenv("GOOGLE_CLIENT_SECRET"))

    google_authorize_url: str = Field(os.getenv("GOOGLE_AUTHORIZE_URL"))
    google_access_token_url: str = Field(os.getenv("GOOGLE_ACCESS_TOKEN_URL"))
    google_userinfo_endpoint: str = Field(os.getenv("GOOGLE_USERINFO_ENDPOINT"))

    access_token_filetime: int = Field(os.getenv("ACCESS_TOKEN_LIFETIME"))
    refresh_token_filetime: int = Field(os.getenv("REFRESH_TOKEN_LIFETIME"))
    auth_history_per_page: int = 10


class Jaeger(BaseSettings):
    JAEGER_TYPE: str = "const"
    REPORTING_HOST: str = "jaeger"
    REPORTING_PORT: int = 6831
    SERVICE_NAME: str = "auth_app"


jaeger_settings = Jaeger()
settings = Settings()
