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

    google_client_id: str = Field(os.getenv("GOOGLE_CLIENT_ID"))
    google_client_secret: str = Field(os.getenv("GOOGLE_CLIENT_SECRET"))

    access_token_filetime: int = Field(os.getenv("ACCESS_TOKEN_LIFETIME"))
    refresh_token_filetime: int = Field(os.getenv("REFRESH_TOKEN_LIFETIME"))
    auth_history_per_page: int = 10


settings = Settings()
