from db.models import User
from db.db import db
from sqlalchemy import exc


def register_new_user(user_login: str, password: str):
    new_user = User(email=user_login, password=password)
    try:
        db.session.add(new_user)
        db.session.commit()
    except exc.IntegrityError as Err:
        # Constraint unique violation
        if Err.orig.pgcode == "23505":
            db.session.rollback()
            return "USER_EXISTS"
        else:
            raise


def login_user(user_login: str, password: str):
    for i in db.session.query(User).all():
        pass
