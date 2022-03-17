# Сообщения ошибок
from enum import IntEnum
from http import HTTPStatus


class APIBaseEnum(IntEnum):

    def __new__(cls, value, phrase, http_status, description=''):
        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.phrase = phrase
        obj.http_status = http_status
        obj.description = description
        return obj


class APIErrors(APIBaseEnum):

    REF_TOK_INVALID_ERROR = 4001, "REF_TOK_INVALID_ERROR", HTTPStatus.BAD_REQUEST, "Invalid ref token"

    AUTH_FAILED = 4011, "AUTH_FAILED", HTTPStatus.UNAUTHORIZED, "Unauthorized"
    NO_JTI_ERROR = 4012, "NO_JTI_ERROR", HTTPStatus.UNAUTHORIZED, "Unauthorized"

    FORBIDDEN = 4031, "FORBIDDEN", HTTPStatus.FORBIDDEN, "Forbidden"

    ROLE_OR_USER_NOT_FOUND = 4041, "USER_OR_ROLE_NOT_FOUND", HTTPStatus.NOT_FOUND, "User or role not found"
    USER_NOT_FOUND = 4042, "USER_NOT_FOUND", HTTPStatus.NOT_FOUND, "User not found"
    ROLE_NOT_FOUND = 4043, "ROLE_NOT_FOUND", HTTPStatus.NOT_FOUND, "Role not fount"

    ROLE_ASSIGNED = 4091, "ROLE_ASSIGNED_TO_USER", HTTPStatus.CONFLICT, "Role already assigned to user"
    ROLE_EXISTS = 4092, "ROLE_EXISTS", HTTPStatus.CONFLICT, "Role already exists"
    ROLE_NAME_ALREADY_TAKEN = 4093, "ROLE_NAME_ALREADY_TAKEN", HTTPStatus.CONFLICT, "Role already exists"
    USER_EXISTS = 4094, "USER_EXISTS", HTTPStatus.CONFLICT, "User already exists"


class APISuccess(APIBaseEnum):

    USER_ALREADY_LOGGED_IN = 2001, "USER_ALREADY_LOGGED_IN", HTTPStatus.OK, "User already logged in"
    OK = 2011, "OK", HTTPStatus.OK, "OK"
    USER_DOESNT_HAVE_ROLE = 2041, "USER_DOESNT_HAVE_ROLE", HTTPStatus.NO_CONTENT, "User does not have this role"
