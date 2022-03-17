import logging
from datetime import timedelta
from functools import wraps

import click
from flask import jsonify
from flask.cli import with_appcontext
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import decode_token
from flask_jwt_extended import get_jti
from flask_jwt_extended import get_jwt
from flask_jwt_extended import verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash

from core.config import settings
from db.db import db
from db.db import redis_db_acc_tok, redis_db_ref_tok
from db.models import User, AuthHistory

jwt = JWTManager()


# Here is a custom decorator that verifies the JWT is present in the request,
# as well as insuring that the JWT has a claim indicating that this user is
# an administrator
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["is_administrator"]:
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins only!"), 403

        return decorator

    return wrapper


# Callback function to check if a JWT exists in the redis blocklist
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    if jwt_payload["type"] == "refresh":
        return False
    jti = jwt_payload["jti"]
    logging.debug(f"==== CHECK FOR REVOKED JTI: {jti}")
    token_in_redis = redis_db_acc_tok.get(jti)
    return token_in_redis is not None


@click.command()
@click.argument("user_login")
@click.argument("password")
@with_appcontext
def register_new_user(user_login: str, password: str):

    user = User.query.filter_by(email=user_login).first()
    if user:
        click.echo("ERR: USER EXISTS")
        return "USER_EXISTS"
    hashed_pass = generate_password_hash(password)
    new_user = User(email=user_login, password=hashed_pass)

    db.session.add(new_user)
    db.session.commit()
    click.echo("DONE")


def login_user(user_login: str, password: str, user_agent: str, host: str):

    user = User.query.filter_by(email=user_login).first()

    if not user:
        logging.debug("==== NO USER WITH THIS EMAIL")
        return "AUTH_FAILED"

    auth_record = AuthHistory(user_id=user.id, user_agent=user_agent, host=host)
    if not check_password_hash(user.password, password):
        logging.debug("==== WRONG PASSWORD")
        auth_record.auth_result = "denied"
        db.session.add(auth_record)
        db.session.commit()
        return "AUTH_FAILED"

    access_token = create_access_token(identity=user_login)
    refresh_token = create_refresh_token(identity=user_login)

    refresh_token_id = get_jti(refresh_token)
    logging.debug(f"==== REFRESH TOKEN: {refresh_token_id}")
    redis_db_ref_tok.set(
        refresh_token_id,
        refresh_token,
        ex=timedelta(minutes=settings.refresh_token_filetime),
    )

    auth_record.auth_result = "success"
    db.session.add(auth_record)
    db.session.commit()

    return access_token, refresh_token


def get_auth_history(user_identy, page):
    user = User.query.filter_by(email=user_identy).first()
    if not user:
        return "NO_SUCH_USER"

    user_id = user.id
    auth_history = AuthHistory.query.filter_by(user_id=user_id).paginate(
        page=page,
        per_page=settings.auth_history_per_page
    )

    result = []
    for record in auth_history:
        di = {
            "date": record.create_at,
            "ip_address": record.host,
            "user_agent": record.user_agent,
            "result": record.auth_result,
        }
        result.append(di)

    return jsonify(result)


def logout_user(jwt_access_token, jwt_refresh_token):
    jti_access = decode_token(jwt_access_token).get("jti")
    logging.debug(f"==== LOGOUT FUNCTION; AFTER JTI ACCESS: {jti_access}")
    jti_refresh = decode_token(jwt_refresh_token).get("jti")
    logging.debug(f"==== LOGOUT FUNCTION; AFTER JTI REFRESH {jti_refresh}")

    if jti_access is None or jti_refresh is None:
        return "NO_JTI_ERROR"

    logging.debug("==== setting redis acc token and del ref token")
    redis_db_acc_tok.set(
        jti_access,
        jwt_access_token,
        ex=timedelta(minutes=settings.access_token_filetime),
    )
    redis_db_ref_tok.delete(jti_refresh)
    logging.debug("==== working with redis done")


def refresh_access_token(identy, jti):
    jti_ref_tok = redis_db_ref_tok.get(jti)
    if jti_ref_tok is None:
        return "REF_TOK_INVALID_ERROR"
    redis_db_ref_tok.delete(jti)

    refresh_token = create_refresh_token(identity=identy)
    access_token = create_access_token(identity=identy)

    refresh_token_id = get_jti(refresh_token)
    redis_db_ref_tok.set(
        refresh_token_id,
        refresh_token,
        ex=timedelta(minutes=settings.refresh_token_filetime),
    )

    return access_token, refresh_token


def update_user(user_id, username, password):
    check_user = User.query.filter(
        (User.email == username) & (User.id != user_id)
    ).first()
    if check_user is not None:
        logging.debug(f"==== check_user: {check_user}")
        return "USER_EXISTS"

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return "USER_NOT_FOUND"

    hashed_pass = generate_password_hash(password)

    user.email = username
    user.password = hashed_pass

    db.session.commit()


def get_user_id_by_email(email: str):
    user = User.query.filter_by(email=email).first()
    if user is None:
        return "USER_NOT_FOUND"

    return user.id


def get_user_email_by_id(user_id: str):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return "USER_NOT_FOUND"

    return user.email
