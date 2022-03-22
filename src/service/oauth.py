from authlib.integrations.flask_client import OAuth

oauth = OAuth()

oauth.register(
    name="yandex",
    authorize_url="https://oauth.yandex.ru/authorize",
    client_kwargs={
        "scope": "login:email"
    }
)
