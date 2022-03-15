import sys
import json
import psycopg2
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


def test_update_email_or_password():
    with psycopg2.connect(**test_settings.dsl) as pg_conn:
        curr = pg_conn.cursor()
        curr.execute("""SELECT id FROM users WHERE email='user1@mail.com';""")
        id = curr.fetchone()
        pg_conn.commit()
        curr.close()
    body = json.dumps({
        "id": id[0],
        "username": "user2@mail.com",
        "password": "P@ssw0rd2"
    })
    headers = {'Content-Type': 'application/json'}
    res = requests.put(
        url=f'{test_settings.auth_api_host}/user',
        data=body,
        headers=headers
    )
    assert res.status_code == HTTPStatus.OK
    body = json.dumps({
        "id": id[0],
        "username": "user2@mail.com",
        "password": "P@ssw0rd2"
    })
    res = requests.put(
        url=f'{test_settings.auth_api_host}/user/',
        data=body,
        headers=headers
    )
    assert res.status_code == HTTPStatus.CONFLICT
    body = json.dumps({
        "id": id[0],
        "username": "user1@mail.com",
        "password": "P@ssw0rd2"
    })
    res = requests.put(
        url=f'{test_settings.auth_api_host}/user/',
        data=body,
        headers=headers
    )
    assert res.status_code == HTTPStatus.OK


def test_refresh_access():
    res = requests.post(
        url=f'{test_settings.auth_api_host}/user/refresh',
    )
    assert res.status_code == HTTPStatus.OK


def test_auth_history():
    res = requests.get(
        url=f'{test_settings.auth_api_host}/user/auth_history',
    )
    assert res.status_code == HTTPStatus.OK


def test_logout():
    res = requests.post(
        url=f'{test_settings.auth_api_host}/user/logout'
    )
    assert res.status_code == HTTPStatus.OK
