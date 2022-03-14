from flask import Blueprint, request, Response
from service.user_logic import register_new_user, login_user, logout_user, refresh_access_token

from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_jwt
from flask_jwt_extended import set_refresh_cookies
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import unset_jwt_cookies


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


@user.route("/login", methods=["POST"])
@jwt_required(optional=True)
def login():
    if request.method == "POST":
        request_data = request.get_json()

        username = request_data["email"]
        password = request_data["password"]

        if username is None or password is None:
            return Response(status=400, mimetype="application/json")

        identy = get_jwt_identity()
        if identy:
            return Response(response="User already logged in", status=200, mimetype="application/json")

        result = login_user(username, password)
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
def refresh_access_token():
    identy = get_jwt_identity()
    jti = get_jwt()["jti"]
    result = refresh_access_token(identy, jti)



@user.route("/auth_history", methods=["GET"])
@jwt_required()
def get_auth_history():
    # verify_jwt_in_request(refresh=False)
    identy = get_jwt_identity()
    s = ""
    for i, j in get_jwt().items():
        s = s + f"- {i}: {j}\n"
    verify_jwt_in_request(refresh=True)
    identy2 = get_jwt_identity()
    s2 = ""
    for i, j in get_jwt().items():
        s2 = s2 + f"- {i}: {j}\n"
    return Response(response=f"IDENTY: {identy}\n{s}\nIDENTY2: {identy2}\n{s2}", status=200, mimetype="application/json")
