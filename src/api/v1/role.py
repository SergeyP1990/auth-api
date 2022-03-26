from http import HTTPStatus

from flask import Blueprint, request, Response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

import service.role_logic as service_role
from service.user_logic import required_role
from api.v1.error_messages import APIErrors, APISuccess

role_routes = Blueprint("role_routes", __name__, url_prefix="/role")


@role_routes.route("/", methods=["GET", "POST"])
@required_role("admin")
def role():

    if request.method == "POST":
        request_data = request.get_json()
        role_name = request_data["name"]

        if role_name is None:
            return Response(status=HTTPStatus.BAD_REQUEST, mimetype="application/json")

        result = service_role.add_role(role_name)
        return Response(status=result.http_status, mimetype="application/json")

    if request.method == "GET":
        query = service_role.list_role()
        return jsonify(query)


@role_routes.route("/<role_id>", methods=["GET", "PUT", "DELETE"])
@required_role("admin")
def role_crud(role_id):

    if request.method == "PUT":
        request_data = request.get_json()
        role_name = request_data["name"]
        change = service_role.change_role(role_id, role_name)
        return Response(status=change.http_status, mimetype="application/json")

    if request.method == "DELETE":
        res = service_role.delete_role(role_id)
        return Response(status=res.http_status, mimetype="application/json")

    if request.method == "GET":
        role_result = service_role.role_by_id(role_id)
        if isinstance(role_result, APIErrors):
            return Response(status=role_result.http_status, mimetype="application/json")
        return role_result


@role_routes.route("/user/<user_id>/role/<role_id>", methods=["PUT", "DELETE"])
@required_role("admin")
def user_role_crud(user_id, role_id):

    if request.method == "PUT":
        assign = service_role.assign_user_role(user_id=user_id, role_id=role_id)
        return Response(status=assign.http_status, mimetype="application/json")

    if request.method == "DELETE":
        assign = service_role.delete_user_role(user_id=user_id, role_id=role_id)
        return Response(status=assign.http_status, mimetype="application/json")


@role_routes.route("/user/<user_id>/role/<role_id>", methods=["GET"])
@required_role("admin", "role_checker")
def user_role_get(user_id, role_id):
    identy = get_jwt_identity()
    if (
        service_role.check_user_role_by_email(identy, "role_checker") != APISuccess.OK
        and service_role.check_user_role_by_email(identy, "admin") != APISuccess.OK
    ):
        return Response(status=HTTPStatus.FORBIDDEN, mimetype="application/json")
    check = service_role.check_user_role(user_id=user_id, role_id=role_id)

    return Response(status=check.http_status, mimetype="application/json")


@role_routes.route("/user/role_check", methods=["GET"])
def user_role_check():
    identy = get_jwt_identity()
    request_data = request.get_json()
    title = request_data['film_title']
    if service_role.check_user_role_by_email(identy, "subscriber") == APISuccess.OK:
        return Response(status=HTTPStatus.OK, mimetype="application/json")
    elif service_role.check_user_role_by_email(identy, f"{title}_rent") == APISuccess.OK:
        return Response(status=HTTPStatus.OK, mimetype="application/json")
    elif service_role.check_user_role_by_email(identy, f"{title}_purchase") == APISuccess.OK:
        return Response(status=HTTPStatus.OK, mimetype="application/json")
    else:
        return Response(status=HTTPStatus.NO_CONTENT, mimetype="application/json")
