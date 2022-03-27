import abc
import enum

from authlib.integrations.flask_client import OAuth

from core.config import settings


class BaseOauthProvider:
    @classmethod
    @abc.abstractmethod
    def get_user_id(cls, data):
        pass

    @classmethod
    @abc.abstractmethod
    def get_email(cls, data):
        pass

    @classmethod
    @abc.abstractmethod
    def get_name(cls):
        pass


class YandexOauthProvider(BaseOauthProvider):
    @classmethod
    def get_user_id(cls, data):
        return data.get("id")

    @classmethod
    def get_email(cls, data):
        return data.get("emails")[0]

    @classmethod
    def get_name(cls):
        return OAuthProviders.YANDEX.value


class GoogleOauthProvider(BaseOauthProvider):
    @classmethod
    def get_user_id(cls, data):
        return data.get("sub")

    @classmethod
    def get_email(cls, data):
        return data.get("email")

    @classmethod
    def get_name(cls):
        return OAuthProviders.GOOGLE.value


class OAuthProviders(enum.Enum):
    def __new__(cls, value, provider):
        obj = object.__new__(cls)
        obj._value_ = value

        obj.provider = provider
        return obj

    YANDEX = "yandex", YandexOauthProvider
    GOOGLE = "google", GoogleOauthProvider


oauth = OAuth()

oauth.register(
    name=OAuthProviders.YANDEX.value,
    authorize_url=settings.yandex_authorize_url,
    access_token_url=settings.yandex_access_token_url,
    userinfo_endpoint=settings.yandex_userinfo_endpoint,
    client_kwargs={"scope": "login:email"},
)

oauth.register(
    name=OAuthProviders.GOOGLE.value,
    authorize_url=settings.google_authorize_url,
    access_token_url=settings.google_access_token_url,
    userinfo_endpoint=settings.google_userinfo_endpoint,
    client_kwargs={"scope": "email"},
)
