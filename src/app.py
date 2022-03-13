from flask import Flask

from db.db import init_db, db


def create_app():
    app = Flask(__name__)
    init_db(app)
    app.app_context().push()
    db.create_all()

    from api.v1 import user, role
    app.register_blueprint(user.user_register)
    app.register_blueprint(role.role_routes)
    return app


app = create_app()
