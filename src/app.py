import logging
from datetime import timedelta

from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate

from core.config import settings
from db.db import init_db, db
from middleware import init_trace
from service.oauth import oauth
from service.role_logic import assign_superuser
from service.user_logic import jwt
from service.user_logic import register_new_user_cli


def create_app():
    logging.getLogger("app")
    logging.basicConfig(level=logging.DEBUG)

    app = Flask(__name__)

    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["1200 per hour", "20 per minute", "1 per second"]
    )

    limiter.init_app(app)
    init_db(app)
    init_trace(app)

    app.app_context().push()

    migrate = Migrate(app, db)
    db.create_all()

    # Here you can globally configure all the ways you want to allow JWTs to
    # be sent to your web application. By default, this will be only headers.
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

    # If true this will only allow the cookies that contain your JWTs to be sent
    # over https. In production, this should always be set to True
    app.config["JWT_COOKIE_SECURE"] = False

    app.config["JWT_SECRET_KEY"] = settings.jwt_secret

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        minutes=settings.access_token_filetime
    )
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(
        minutes=settings.refresh_token_filetime
    )

    app.config["JWT_REFRESH_CSRF_HEADER_NAME"] = "X-CSRF-TOKEN-REF"

    app.config["YANDEX_CLIENT_ID"] = settings.yandex_client_id
    app.config["YANDEX_CLIENT_SECRET"] = settings.yandex_client_secret

    app.config["GOOGLE_CLIENT_ID"] = settings.google_client_id
    app.config["GOOGLE_CLIENT_SECRET"] = settings.google_client_secret

    app.config["SECRET_KEY"] = settings.flask_secret

    from api.v1 import user, role

    app.register_blueprint(user.user)
    app.register_blueprint(role.role_routes)

    oauth.init_app(app)
    jwt.init_app(app)

    app.cli.add_command(register_new_user_cli)
    app.cli.add_command(assign_superuser)

    return app


application = create_app()


@application.before_request
def before_request():
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        raise RuntimeError('request id is requred')
