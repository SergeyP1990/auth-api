import enum
from authlib.integrations.flask_client import OAuth

from core.config import settings


oauth = OAuth()


class ProvidersNames(enum.Enum):
    YANDEX = "yandex"
    GOOGLE = "google"


oauth.register(
    name=ProvidersNames.YANDEX.value,
    authorize_url=settings.yandex_authorize_url,
    access_token_url=settings.yandex_access_token_url,
    userinfo_endpoint=settings.yandex_userinfo_endpoint,
    client_kwargs={"scope": "login:email"},
)

oauth.register(
    name=ProvidersNames.GOOGLE.value,
    authorize_url=settings.google_authorize_url,
    access_token_url=settings.google_access_token_url,
    userinfo_endpoint=settings.google_userinfo_endpoint,
    client_kwargs={"scope": "email"},
)
