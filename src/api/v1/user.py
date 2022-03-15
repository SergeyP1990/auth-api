from flask import Blueprint, request, Response
from service.user_logic import register_new_user, login_user, logout_user, refresh_access_token
from service.user_logic import update_user, get_auth_history, get_user_id_by_email

from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_jwt
from flask_jwt_extended import set_refresh_cookies
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import unset_jwt_cookies

from service.role_logic import check_user_role_by_email

import logging

user = Blueprint("user", __name__, url_prefix="/user")


@user.route("/register", methods=["POST"])
def register():
    if request.method == "POST":
        request_data = request.get_json()

        username = request_data["username"]
        password = request_data["password"]

        if username is None or password is None:
            return Response(status=400, mimetype="application/json")

        result = register_new_user(username, password)
        if result == "USER_EXISTS":
            return Response(status=409, mimetype="application/json")

        return Response(status=200, mimetype="application/json")


@user.route("/", methods=["PUT"])
@jwt_required()
def update_login_password():
    if request.method == "PUT":
        request_data = request.get_json()

        user_id = request_data["user_id"]
        username = request_data["email"]
        password = request_data["password"]

        current_user_identy = get_jwt_identity()
        current_user_id = get_user_id_by_email(current_user_identy)
        if user_id != current_user_id:
            if check_user_role_by_email(current_user_identy, "admin") != "OK":
                return Response(status=403, mimetype="application/json")

        if username is None or password is None or user_id is None:
            return Response(status=400, mimetype="application/json")

        result = update_user(user_id, username, password)
        if result == "USER_NOT_FOUND":
            return Response(status=404, mimetype="application/json")
        if result == "USER_EXISTS":
            return Response(status=409, mimetype="application/json")

        return Response(status=200, mimetype="application/json")


@user.route("/login", methods=["POST"])
@jwt_required(optional=True)
def login():
    if request.method == "POST":
        request_data = request.get_json()

        username = request_data["email"]
        password = request_data["password"]

        user_agent = request.headers["User-Agent"]
        host = request.headers["Host"]

        if username is None or password is None:
            return Response(status=400, mimetype="application/json")

        identy = get_jwt_identity()
        if identy:
            return Response(response="User already logged in", status=200, mimetype="application/json")

        result = login_user(username, password, user_agent, host)
        if result == "AUTH_FAILED":
            return Response(status=401, mimetype="application/json")

        resp = Response(status=200, mimetype="application/json")

        set_access_cookies(resp, result[0])
        set_refresh_cookies(resp, result[1])
        return resp


# Endpoint for revoking the current users access token. Save the JWTs unique
# identifier (jti) in redis. Also set a Time to Live (TTL)  when storing the JWT
# so that it will automatically be cleared out of redis after the token expires.
@user.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    acc_cookie = request.cookies.get("access_token_cookie")
    ref_cookie = request.cookies.get("refresh_token_cookie")
    result = logout_user(acc_cookie, ref_cookie)

    if result == "NO_JTI_ERROR":
        return Response(status=401, mimetype="application/json")

    resp = Response(status=200, mimetype="application/json")
    unset_jwt_cookies(resp)

    return resp


@user.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_tokens():
    identy = get_jwt_identity()
    jti = get_jwt()["jti"]
    result = refresh_access_token(identy, jti)

    if result == "NO_JTI_ERROR":
        return Response(status=401, mimetype="application/json")

    resp = Response(status=200, mimetype="application/json")
    set_access_cookies(resp, result[0])
    set_refresh_cookies(resp, result[1])

    return resp


@user.route("/auth_history", methods=["GET"])
@jwt_required()
def auth_history():
    identy = get_jwt_identity()

    result = get_auth_history(identy)

    if result == "NO_SUCH_USER":
        return Response(status=404, mimetype="application/json")

    logging.debug(f"==== RESULT: {result}")

    result.status = 200
    result.mimetype = "application/json"
    return result
