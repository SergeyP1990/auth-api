from flask import Flask

from db.db import init_db, db
from db.models import User
from flask_jwt_extended import JWTManager

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from service.user_logic import jwt
import sys
from service.user_logic import register_new_user
from service.role_logic import assign_user_role_by_name
from api.v1.error_messages import APIErrors


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
    
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=5000)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=7000)

    app.config["JWT_REFRESH_CSRF_HEADER_NAME"] = "X-CSRF-TOKEN-REF"

    from api.v1 import user, role
    app.register_blueprint(user.user)
    app.register_blueprint(role.role_routes)
    
    jwt.init_app(app)
    
    return app

  
app = create_app()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        exit(0)
    if sys.argv[1] == "register-user":
        if len(sys.argv) < 4:
            print(f"Usage: {sys.argv[0]} register-user <user_name> <password>")
            exit(0)
        user_login = sys.argv[2]
        user_password = sys.argv[3]
        register_new_user(user_login, user_password)
    if sys.argv[1] == "grant-superuser":
        if len(sys.argv) < 3:
            print(f"Usage: {sys.argv[0]} grant-superuser <user_name>")
            exit(0)
        result = assign_user_role_by_name(sys.argv[2], "superadmin")
        if isinstance(result, APIErrors):
            print(f"ERROR: {result}")
            exit(1)
        print("Role granted")
        exit(0)

