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
from flask_jwt_extended import decode_token

from db.db import redis_db_acc_tok, redis_db_ref_tok

jwt = JWTManager()


# Callback function to check if a JWT exists in the redis blocklist
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    print("==== CHECK IF TOKEN REVOKED FUNCTION CALL")
    if jwt_payload["type"] == "refresh":
        return False
    jti = jwt_payload["jti"]
    print(f"==== JTI: {jti}")
    token_in_redis = redis_db_acc_tok.get(jti)
    return token_in_redis is not None


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
    # print(f"==== REDIS REFRESH TOKEN: {redis_db_ref_tok.get(refresh_token_id)}")

    return access_token, refresh_token


def logout_user(jwt_access_token, jwt_refresh_token):
    jti_access = decode_token(jwt_access_token).get("jti")
    print(f"==== LOGOUT FUNCTION; AFTER JTI ACCESS: {jti_access}")
    jti_refresh = decode_token(jwt_refresh_token).get("jti")
    print(f"==== LOGOUT FUNCTION; AFTER JTI REFRESH {jti_refresh}")

    if jti_access is None or jti_refresh is None:
        return "NO_JTI_ERROR"

    print("==== setting redis acc token and del def token")
    redis_db_acc_tok.set(jti_access, jwt_access_token, ex=timedelta(seconds=5000))
    redis_db_ref_tok.delete(jti_refresh)
    print("==== working with redis done")


def refresh_access_token(identy, jti):
    jti_ref_tok = redis_db_ref_tok.get(jti)
    if jti_ref_tok is None:
        return "REF_TOK_INVALID_ERROR"
    redis_db_ref_tok.delete(jti)

    refresh_token = create_refresh_token(identity=identy)
    access_token = create_access_token(identity=identy)

    refresh_token_id = get_jti(refresh_token)
    redis_db_ref_tok.set(refresh_token_id, refresh_token, ex=timedelta(seconds=7000))

    return access_token, refresh_token
