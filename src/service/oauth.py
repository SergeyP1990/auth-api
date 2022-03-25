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
