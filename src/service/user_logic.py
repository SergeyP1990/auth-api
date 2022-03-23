import logging
from datetime import timedelta
from functools import wraps

import click
from flask import jsonify, Response
from flask.cli import with_appcontext
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import decode_token
from flask_jwt_extended import get_jti
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash

from core.config import settings
from db.db import db
from db.db import redis_db_acc_tok, redis_db_ref_tok
from db.models import User, AuthHistory
from api.v1.error_messages import APISuccess, APIErrors
from service.role_logic import check_user_role_by_email, check_user_role, Role

jwt = JWTManager()


def required_role(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identy = get_jwt_identity()

            superadmin_check = check_user_role_by_email(identy, "superadmin")
            if superadmin_check == APISuccess.OK:
                return fn(*args, **kwargs)
            else:
                for role_name in roles:
                    logging.debug(f"CHECKING ROLE {role_name} ON USER {identy}")
                    check_role = check_user_role_by_email(identy, role_name)
                    if check_role == APISuccess.OK:
                        logging.debug(f"CHECKS GOOD {check_role.phrase}")
                        return fn(*args, **kwargs)
                    logging.debug(f"CHECKS FAIL {check_role.phrase}")
                    return Response(status=APIErrors.FORBIDDEN.http_status, mimetype="application/json")
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


def register_new_user(user_login: str, password: str):

    user = User.query.filter_by(email=user_login).first()
    if user:
        return APIErrors.USER_EXISTS
    hashed_pass = generate_password_hash(password)
    new_user = User(email=user_login, password=hashed_pass)

    db.session.add(new_user)
    db.session.commit()
    return APISuccess.OK


@click.command()
@click.argument("user_login")
@click.argument("password")
@with_appcontext
def register_new_user_cli(user_login: str, password: str):

    result = register_new_user(user_login, password)
    if isinstance(result, APIErrors):
        click.echo(f"ERROR: {result.phrase}: {result.description}")
        raise click.Abort
    if isinstance(result, APISuccess):
        click.echo("DONE")
        return


def login_user(user_login: str,
               password: str,
               user_agent: str,
               host: str,
               user_platform: str
               ):

    user = User.query.filter_by(email=user_login).first()

    if not user:
        logging.debug("==== NO USER WITH THIS EMAIL")
        return APIErrors.AUTH_FAILED

    auth_record = AuthHistory(user_id=user.id,
                              user_agent=user_agent,
                              host=host,
                              user_platform=user_platform
                              )
    if not check_password_hash(user.password, password):
        logging.debug("==== WRONG PASSWORD")
        auth_record.auth_result = "denied"
        db.session.add(auth_record)
        db.session.commit()
        return APIErrors.AUTH_FAILED

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
        return APIErrors.USER_NOT_FOUND

    user_id = user.id
    auth_history = AuthHistory.query.filter_by(user_id=user_id).paginate(
        page=page,
        per_page=settings.auth_history_per_page
    ).items

    result = []
    for record in auth_history:
        di = {
            "date": record.create_at,
            "ip_address": record.host,
            "user_agent": record.user_agent,
            "result": record.auth_result,
            "user_platform": record.user_platform,
        }
        result.append(di)

    return jsonify(result)


def logout_user(jwt_access_token, jwt_refresh_token):
    jti_access = decode_token(jwt_access_token).get("jti")
    logging.debug(f"==== LOGOUT FUNCTION; AFTER JTI ACCESS: {jti_access}")
    jti_refresh = decode_token(jwt_refresh_token).get("jti")
    logging.debug(f"==== LOGOUT FUNCTION; AFTER JTI REFRESH {jti_refresh}")

    if jti_access is None or jti_refresh is None:
        return APIErrors.NO_JTI_ERROR

    logging.debug("==== setting redis acc token and del ref token")
    redis_db_acc_tok.set(
        jti_access,
        jwt_access_token,
        ex=timedelta(minutes=settings.access_token_filetime),
    )
    redis_db_ref_tok.delete(jti_refresh)
    logging.debug("==== working with redis done")

    return APISuccess.OK


def refresh_access_token(identy, jti):
    jti_ref_tok = redis_db_ref_tok.get(jti)
    if jti_ref_tok is None:
        return APIErrors.REF_TOK_INVALID_ERROR
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
        return APIErrors.USER_EXISTS

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return APIErrors.USER_NOT_FOUND

    hashed_pass = generate_password_hash(password)

    user.email = username
    user.password = hashed_pass

    db.session.commit()

    return APISuccess.OK


def get_user_id_by_email(email: str):
    user = User.query.filter_by(email=email).first()
    if user is None:
        return APIErrors.USER_NOT_FOUND

    return user.id


def get_user_email_by_id(user_id: str):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return APIErrors.USER_NOT_FOUND

    return user.email
