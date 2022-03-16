import os
from dataclasses import dataclass

from multidict import CIMultiDictProxy
from pydantic import BaseSettings, Field


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


class TestSettings(BaseSettings):
    redis_host: str = Field(os.getenv("REDIS_HOST"))
    redis_port: str = Field(os.getenv("REDIS_PORT"))

    auth_api_host: str = Field(os.getenv("AUTH_API_HOST"))

    dsl = {
        "dbname": os.environ.get("POSTGRES_DB"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "host": os.environ.get("POSTGRES_HOST"),
        "port": os.environ.get("POSTGRES_PORT"),
    }


test_settings = TestSettings()
