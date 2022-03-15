import service.role_logic as service_role
from api.v1.error_messages import APIErrors
from flask import Blueprint, request, Response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

role_routes = Blueprint("role", __name__, url_prefix="/role")


@role_routes.route("/", methods=["GET", "POST"])
@jwt_required()
def role():
    identy = get_jwt_identity()
    service_role.check_user_role_by_email(identy, "admin")
    if request.method == "POST":
        request_data = request.get_json()
        role_name = request_data["name"]

        if role_name is None:
            return Response(status=400, mimetype="application/json")

        result = service_role.add_role(role_name)
        if result == APIErrors.ROLE_EXISTS:
            return Response(status=409, mimetype="application/json")

        return Response(status=200, mimetype="application/json")

    if request.method == "GET":
        query = service_role.list_role()
        return jsonify(query)


@role_routes.route("/<role_id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def role_crud(role_id):
    identy = get_jwt_identity()
    service_role.check_user_role_by_email(identy, "admin")
    if request.method == "PUT":
        request_data = request.get_json()
        role_name = request_data["name"]
        change = service_role.change_role(role_id, role_name)
        if change == APIErrors.ROLE_OR_USER_NOT_FOUND:
            return Response(status=404, mimetype="application/json")
        return Response(status=200, mimetype="application/json")

    if request.method == "DELETE":
        service_role.delete_role(role_id)
        return Response(status=200, mimetype="application/json")

    if request.method == "GET":
        role = service_role.role_by_id(role_id)
        print(role)
        if role == APIErrors.ROLE_OR_USER_NOT_FOUND:
            return Response(status=400, mimetype="application/json")
        return role


@role_routes.route("/user/<user_id>/role/<role_id>",
                   methods=["PUT", "DELETE"])
@jwt_required()
def user_role_crud(user_id, role_id):
    identy = get_jwt_identity()
    service_role.check_user_role_by_email(identy, "admin")
    if request.method == "PUT":
        assign = service_role.assign_user_role(
            user_id=user_id,
            role_id=role_id
        )
        if assign == APIErrors.ROLE_ASSIGNED:
            return Response(status=409, mimetype="application/json")
        if assign == APIErrors.ROLE_OR_USER_NOT_FOUND:
            return Response(status=404, mimetype="application/json")
        return Response(status=200, mimetype="application/json")

    if request.method == "DELETE":
        assign = service_role.delete_user_role(
            user_id=user_id,
            role_id=role_id
        )
        if assign == APIErrors.ROLE_OR_USER_NOT_FOUND:
            return Response(status=404, mimetype="application/json")
        return Response(status=200, mimetype="application/json")


@role_routes.route("/user/<user_id>/role/<role_id>",
                   methods=["GET"])
@jwt_required()
def user_role_get(user_id, role_id):
    check = service_role.check_user_role(
        user_id=user_id,
        role_id=role_id
    )
    if check == APIErrors.ROLE_OR_USER_NOT_FOUND:
        return Response(status=404, mimetype="application/json")
    if check == APIErrors.USER_DOESNT_HAVE_ROLE:
        return Response(status=400, mimetype="application/json")
    if check == "OK":
        return Response(status=200, mimetype="application/json")
