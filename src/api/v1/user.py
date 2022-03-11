from flask import Blueprint, request, Response
from service.user_logic import register_new_user, login_user

user_register = Blueprint("user_register", __name__, url_prefix="/user")


@user_register.route("/register", methods=["POST"])
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


@user_register.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        request_data = request.get_json()

        username = request_data["username"]
        password = request_data["password"]

        if username is None or password is None:
            return Response(status=400, mimetype="application/json")

        result = login_user(username, password)
        if result == "AUTH_FAILED":
            return Response(status=401, mimetype="application/json")

        return Response(status=200, mimetype="application/json")
