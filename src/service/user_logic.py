from db.models import User
from db.db import db
from sqlalchemy import exc
from werkzeug.security import generate_password_hash, check_password_hash


def register_new_user(user_login: str, password: str):

    user = User.query.filter_by(email=user_login).first()
    if user:
        return "USER_EXISTS"
    hashed_pass = generate_password_hash(password)
    new_user = User(email=user_login, password=hashed_pass)

    # try:
    db.session.add(new_user)
    db.session.commit()
    # except exc.IntegrityError as Err:
    #     # Constraint unique violation
    #     if Err.orig.pgcode == "23505":
    #         db.session.rollback()
    #
    #     else:
    #         raise


def login_user(user_login: str, password: str):

    user = User.query.filter_by(email=user_login).first()

    if not user or not check_password_hash(user.password, password):
        return "AUTH_FAILED"
