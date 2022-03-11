from flask import Blueprint, request, Response

role = Blueprint("role", __name__, url_prefix="/role")


@role.route("/role", methods=["POST"])
def show_roles():
    pass
