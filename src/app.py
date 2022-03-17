from datetime import timedelta

from flask import Flask
from flask_migrate import Migrate

from core.config import settings
from db.db import init_db, db
from service.role_logic import assign_superuser, add_role
from service.user_logic import jwt
from service.user_logic import register_new_user_cli


def create_app():
    app = Flask(__name__)
    init_db(app)
    migrate = Migrate(app, db)
    app.app_context().push()

    # Here you can globally configure all the ways you want to allow JWTs to
    # be sent to your web application. By default, this will be only headers.
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

    # If true this will only allow the cookies that contain your JWTs to be sent
    # over https. In production, this should always be set to True
    app.config["JWT_COOKIE_SECURE"] = False

    app.config["JWT_SECRET_KEY"] = settings.secret

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        minutes=settings.access_token_filetime
    )
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(
        minutes=settings.refresh_token_filetime
    )

    app.config["JWT_REFRESH_CSRF_HEADER_NAME"] = "X-CSRF-TOKEN-REF"

    from api.v1 import user, role

    app.register_blueprint(user.user)
    app.register_blueprint(role.role_routes)

    jwt.init_app(app)

    # add_role("superadmin")

    app.cli.add_command(register_new_user_cli)
    app.cli.add_command(assign_superuser)

    return app


application = create_app()
