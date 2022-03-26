from authlib.integrations.flask_client import OAuth

oauth = OAuth()

oauth.register(
    name="yandex",
    authorize_url="https://oauth.yandex.ru/authorize",
    access_token_url="https://oauth.yandex.ru/token",
    userinfo_endpoint="https://login.yandex.ru/info",
    client_kwargs={
        "scope": "login:email"
    }
)

oauth.register(
    name="google",
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    client_kwargs={
        "scope": "email"
    }
)
