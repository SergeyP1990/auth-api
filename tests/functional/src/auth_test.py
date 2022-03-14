import sys
import json
from http import HTTPStatus

import requests

sys.path.append('/usr/src/tests/')
from settings import test_settings


def test_login_fail(truncate_table):
    body = json.dumps({"email": "user1@mail.com", "password": "P@ssw0rd"})
    headers = {'Content-Type': 'application/json'}
    res = requests.post(
        url=f'{test_settings.auth_api_host}/user/login',
        data=body,
        headers=headers
    )
    assert res.status_code == HTTPStatus.UNAUTHORIZED


def test_register():
    body = json.dumps({"username": "user1@mail.com", "password": "P@ssw0rd"})
    headers = {'Content-Type': 'application/json'}
    res = requests.post(
        url=f'{test_settings.auth_api_host}/user/register',
        data=body,
        headers=headers
    )
    assert res.status_code == HTTPStatus.OK
    res = requests.post(
        url=f'{test_settings.auth_api_host}/user/register',
        data=body,
        headers=headers
    )
    assert res.status_code == HTTPStatus.CONFLICT


def test_login():
    body = json.dumps({"email": "user1@mail.com", "password": "P@ssw0rd"})
    headers = {'Content-Type': 'application/json'}
    res = requests.post(
        url=f'{test_settings.auth_api_host}/user/login',
        data=body,
        headers=headers
    )
    assert res.status_code == HTTPStatus.OK


def test_auth_history():
    res = requests.get(
        url=f'{test_settings.auth_api_host}/user/auth_history',
    )
    assert res.status_code == HTTPStatus.OK
