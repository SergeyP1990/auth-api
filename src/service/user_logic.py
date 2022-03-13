from db.models import User
from db.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
from datetime import timedelta

from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jti

from db.db import redis_db_acc_tok, redis_db_ref_tok

jwt = JWTManager()


# Callback function to check if a JWT exists in the redis blocklist
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    print(f"==== JTI: {jti}")
    # token_in_redis = jwt_redis_blocklist.get(jti)
    return False


def register_new_user(user_login: str, password: str):

    user = User.query.filter_by(email=user_login).first()
    if user:
        return "USER_EXISTS"
    hashed_pass = generate_password_hash(password)
    new_user = User(email=user_login, password=hashed_pass)

    db.session.add(new_user)
    db.session.commit()


def login_user(user_login: str, password: str):

    user = User.query.filter_by(email=user_login).first()

    if not user or not check_password_hash(user.password, password):
        return "AUTH_FAILED"

    access_token = create_access_token(identity=user_login)
    refresh_token = create_refresh_token(identity=user_login)

    refresh_token_id = get_jti(refresh_token)
    print(f"==== REFRESH TOKEN: {refresh_token_id}")
    redis_db_ref_tok.set(refresh_token_id, refresh_token, ex=timedelta(seconds=7000))

    return access_token, refresh_token


def logout_user(jwt_access_token, jwt_refresh_token):
    pass
