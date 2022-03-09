from db.models import User
from db.db import db


def register_new_user(user_login: str, password: str):
    print("register_new_user called")
    for login in db.session.query(User.email):
        if login == user_login:
            return "USER_EXISTS"

    new_user = User(email=user_login, password=password, phone_number="123123")
    db.session.add(new_user)
    db.session.commit()
