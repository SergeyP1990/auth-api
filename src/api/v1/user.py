import logging
from http import HTTPStatus

from flask import Blueprint, request, Response, url_for
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import set_refresh_cookies
from flask_jwt_extended import unset_jwt_cookies

from api.v1.error_messages import APISuccess, APIErrors
from service.oauth import oauth, OAuthProviders
from service.role_logic import check_user_role_by_email
from service.user_logic import (
    register_new_user,
    login_user,
    logout_user,
    refresh_access_token,
    update_user,
    get_auth_history,
    get_user_id_by_email,
    login_user_social_account,
)

user = Blueprint("user", __name__, url_prefix="/user")


@user.route("/register", methods=["POST"])
def register():
    if request.method == "POST":
        request_data = request.get_json()

        username = request_data["username"]
        password = request_data["password"]

        if username is None or password is None:
            return Response(status=HTTPStatus.BAD_REQUEST, mimetype="application/json")

        result = register_new_user(username, password)

        return Response(
            response=result.description,
            status=result.http_status,
            mimetype="application/json",
        )


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
        if isinstance(current_user_id, APIErrors):
            return Response(
                status=current_user_id.http_status, mimetype="application/json"
            )
        if user_id != current_user_id:
            if check_user_role_by_email(current_user_identy, "admin") != APISuccess.OK:
                return Response(
                    status=HTTPStatus.FORBIDDEN, mimetype="application/json"
                )

        if username is None or password is None or user_id is None:
            return Response(status=HTTPStatus.BAD_REQUEST, mimetype="application/json")

        result = update_user(user_id, username, password)
        if isinstance(result, APIErrors):
            return Response(status=result.http_status, mimetype="application/json")

        return Response(status=HTTPStatus.OK, mimetype="application/json")


@user.route("/login", methods=["POST"])
@jwt_required(optional=True)
def login():
    if request.method == "POST":
        request_data = request.get_json()

        username = request_data["email"]
        password = request_data["password"]

        user_agent = request.headers["User-Agent"]
        host = request.headers["Host"]

        user_platform = request.user_agent.platform
        if username is None or password is None:
            return Response(status=HTTPStatus.BAD_REQUEST, mimetype="application/json")

        identy = get_jwt_identity()
        if identy:
            return Response(
                response=APISuccess.USER_ALREADY_LOGGED_IN.description,
                status=APISuccess.USER_ALREADY_LOGGED_IN.http_status,
                mimetype="application/json",
            )

        result = login_user(username, password, user_agent, host, user_platform)
        if isinstance(result, APIErrors):
            return Response(status=result.http_status, mimetype="application/json")

        resp = Response(status=HTTPStatus.OK, mimetype="application/json")

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

    if isinstance(result, APIErrors):
        return Response(status=result.http_status, mimetype="application/json")

    resp = Response(status=HTTPStatus.OK, mimetype="application/json")
    unset_jwt_cookies(resp)

    return resp


@user.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_tokens():
    identy = get_jwt_identity()
    jti = get_jwt()["jti"]
    result = refresh_access_token(identy, jti)

    if isinstance(result, APIErrors):
        return Response(status=result.http_status, mimetype="application/json")

    resp = Response(status=HTTPStatus.OK, mimetype="application/json")
    set_access_cookies(resp, result[0])
    set_refresh_cookies(resp, result[1])

    return resp


@user.route("/auth_history/", methods=["GET"])
@user.route("/auth_history/page/<int:page>", methods=["GET"])
@jwt_required()
def auth_history(page=1):
    identy = get_jwt_identity()
    result = get_auth_history(identy, page)

    if isinstance(result, APIErrors):
        return Response(status=result.http_status, mimetype="application/json")

    logging.debug(f"==== RESULT: {result}")

    result.status = HTTPStatus.OK
    result.mimetype = "application/json"
    return result


@user.route("/oauth/login/<string:provider>")
def oauth_login(provider):
    if provider is None:
        err = APIErrors.EMPTY_PROVIDER_NAME
        return Response(response=err.description, status=err.http_status, mimetype="application/json")
    if provider not in [prov.value for prov in OAuthProviders]:
        err = APIErrors.UNSUPPORTED_PROVIDER_NAME
        return Response(response=err.description, status=err.http_status, mimetype="application/json")

    client = oauth.create_client(provider)
    redirect_uri = url_for(f"user.oauth_auth", provider=provider, _external=True)
    logging.debug(f"==== REDIRECT URI: {redirect_uri}")
    redirect = client.authorize_redirect(redirect_uri)

    return redirect


@user.route("/oauth/auth/<string:provider>")
def oauth_auth(provider):

    user_agent = request.headers["User-Agent"]
    host = request.headers["Host"]

    client = oauth.create_client(provider)
    oauth_provider = OAuthProviders(provider).provider
    logging.debug(f"==== YA AUTH ARGS: {request.args}")
    token = client.authorize_access_token()
    logging.debug(f"==== TOKEN GET")
    logging.debug(f"==== TOKEN: {token}")

    data = client.userinfo(token=token)
    logging.debug(f"==== DATA: {data}")

    user_id = oauth_provider.get_user_id(data)
    user_email = oauth_provider.get_email(data)
    result = login_user_social_account(
        social_id=user_id,
        social_name=OAuthProviders(provider),
        host=host,
        user_agent=user_agent,
        email=user_email,
    )

    resp = Response(status=HTTPStatus.OK, mimetype="application/json")

    set_access_cookies(resp, result[0])
    set_refresh_cookies(resp, result[1])
    return resp
