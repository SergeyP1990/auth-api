import logging

from api.v1.error_messages import APIErrors
from db.db import db
from db.models import Role, User, UserRole


def add_role(role_name: str):
    role = Role.query.filter_by(name=role_name).first()
    if role:
        return APIErrors.ROLE_EXISTS
    new_role = Role(name=role_name)
    db.session.add(new_role)
    db.session.commit()


def list_role():
    query = Role.query.all()
    role_list = [{"id": role.id,
                  "name": role.name,
                  "create_at": role.create_at,
                  "update_at": role.update_at
                  } for role in query]
    return role_list


def role_by_id(role_id: str):
    query = Role.query.filter_by(id=role_id).first()
    role = {"id": query.id,
            "name": query.name,
            "create_at": query.create_at,
            "update_at": query.update_at
            }
    return role


def change_role(role_id: str, role_name: str):
    role = Role.query.filter_by(id=role_id).first()
    if role is None:
        return APIErrors.ROLE_OR_USER_NOT_FOUND
    check_role = Role.query.filter_by(name=role_name).first()
    if check_role is not None:
        return APIErrors.ROLE_NAME_ALREADY_TAKEN
    role.name = role_name
    db.session.commit()


def delete_role(role_id: str):
    role_to_delete = Role.query.filter_by(id=role_id).first()

    if role_to_delete is None:
        return APIErrors.ROLE_NOT_FOUND

    role_to_delete.delete()
    db.session.commit()


def assign_user_role(user_id: str, role_id: str):
    user = User.query.filter_by(id=user_id)
    role = Role.query.filter_by(id=role_id)

    if user is None or role is None:
        return APIErrors.ROLE_OR_USER_NOT_FOUND

    user_role = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
    if user_role:
        return APIErrors.ROLE_ASSIGNED

    new_user_role = UserRole(user_id=user_id, role_id=role_id)
    db.session.add(new_user_role)
    db.session.commit()


def assign_user_role_by_name(user_name: str, role_name: str):
    user = User.query.filter_by(email=user_name).first()
    role = Role.query.filter_by(name=role_name).first()

    if user is None:
        return APIErrors.USER_NOT_FOUND
    if role is None:
        return APIErrors.ROLE_NOT_FOUND

    return assign_user_role(user.id, role.id)


def check_user_role(user_id: str, role_id: str):
    user = User.query.filter_by(id=user_id)
    role = Role.query.filter_by(id=role_id)
    user_role = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()

    if user is None or role is None:
        logging.debug("check_user_role: user not found")
        return APIErrors.ROLE_OR_USER_NOT_FOUND
    if user_role is None:
        logging.debug("check_user_role: user_role not found")
        return APIErrors.USER_DOESNT_HAVE_ROLE

    return "OK"


def check_user_role_by_email(email: str, role_name: str):
    user = User.query.filter_by(email=email).first()
    role = Role.query.filter_by(name=role_name).first()

    if user is None:
        logging.debug("check_user_role_by_email: user not found")
        return APIErrors.ROLE_OR_USER_NOT_FOUND

    superadmin_role = Role.query.filter_by(name="superadmin").first()
    if superadmin_role is not None:
        is_superadmin = check_user_role(user.id, superadmin_role.id)
        if is_superadmin == "OK":
            return "OK"

    if role is None:
        logging.debug("check_user_role_by_email: role not found")
        return APIErrors.ROLE_OR_USER_NOT_FOUND

    return check_user_role(user.id, role.id)


def delete_user_role(user_id: str, role_id: str):
    user = User.query.filter_by(id=user_id)
    role = Role.query.filter_by(id=role_id)
    user_role = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
    if user is None or role is None or user_role is None:
        return APIErrors.ROLE_OR_USER_NOT_FOUND

    db.session.delete(user_role)
    db.session.commit()
