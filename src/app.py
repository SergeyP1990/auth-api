from flask import Flask
from db.db import init_db, db
from db.models import User
from flask_jwt_extended import JWTManager

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from service.user_logic import jwt


def create_app():
    app = Flask(__name__)
    init_db(app)
    app.app_context().push()
    db.create_all()

    # Here you can globally configure all the ways you want to allow JWTs to
    # be sent to your web application. By default, this will be only headers.
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

    # If true this will only allow the cookies that contain your JWTs to be sent
    # over https. In production, this should always be set to True
    app.config["JWT_COOKIE_SECURE"] = False

    # Change this in your code!
    app.config["JWT_SECRET_KEY"] = "super-secret"

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=5)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=7)

    from api.v1 import user
    app.register_blueprint(user.user)

    jwt.init_app(app)

    return app


app = create_app()
