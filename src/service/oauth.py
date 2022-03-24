from authlib.integrations.flask_client import OAuth

oauth = OAuth()

oauth.register(
    name="yandex",
    authorize_url="https://oauth.yandex.ru/authorize",
    access_token_url="https://oauth.yandex.ru/token",
    client_kwargs={
        "scope": "login:email"
    }
)
