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


def test_refresh_access():
    body = json.dumps({"email": "user1@mail.com", "password": "P@ssw0rd"})
    headers = {'Content-Type': 'application/json'}
    res = requests.post(
        url=f'{test_settings.auth_api_host}/user/login',
        data=body,
        headers=headers
    )
    csrf_access = res.cookies['csrf_access_token']
    csrf_refresh = res.cookies['csrf_refresh_token']
    cookies = res.cookies
    headers = {'Content-Type': 'application/json',
               'X-CSRF-TOKEN': csrf_access,
               'X-CSRF-TOKEN-REF': csrf_refresh}
    res = requests.post(
        url=f'{test_settings.auth_api_host}/user/refresh',
        cookies=cookies,
        headers=headers
    )
    assert res.status_code == HTTPStatus.OK


def test_auth_history():
    body = json.dumps({"email": "user1@mail.com", "password": "P@ssw0rd"})
    headers = {'Content-Type': 'application/json'}
    res = requests.post(
        url=f'{test_settings.auth_api_host}/user/login',
        data=body,
        headers=headers
    )

    csrf_access = res.cookies['csrf_access_token']
    csrf_refresh = res.cookies['csrf_refresh_token']
    cookies = res.cookies
    headers = {'Content-Type': 'application/json',
               'X-CSRF-TOKEN': csrf_access,
               'X-CSRF-TOKEN-REF': csrf_refresh}
    res = requests.get(
        url=f'{test_settings.auth_api_host}/user/auth_history',
        cookies=cookies,
        headers=headers
    )
    assert len(res.content) > 0
    assert res.status_code == HTTPStatus.OK


def test_logout():
    body = json.dumps({"email": "user1@mail.com", "password": "P@ssw0rd"})
    headers = {'Content-Type': 'application/json'}
    res = requests.post(
        url=f'{test_settings.auth_api_host}/user/login',
        data=body,
        headers=headers
    )

    csrf_access = res.cookies['csrf_access_token']
    csrf_refresh = res.cookies['csrf_refresh_token']
    cookies = res.cookies
    headers = {'Content-Type': 'application/json',
               'X-CSRF-TOKEN': csrf_access,
               'X-CSRF-TOKEN-REF': csrf_refresh}

    res = requests.post(
        url=f'{test_settings.auth_api_host}/user/logout',
        cookies=cookies,
        headers=headers
    )
    assert res.status_code == HTTPStatus.OK


def test_update_email_or_password_ok(grunt_user_role):
    body = json.dumps({"email": "user1@mail.com", "password": "P@ssw0rd"})
    headers = {'Content-Type': 'application/json'}
    res = requests.post(
        url=f'{test_settings.auth_api_host}/user/login',
        data=body,
        headers=headers
    )
    assert res.status_code == HTTPStatus.OK

    with psycopg2.connect(**test_settings.dsl) as pg_conn:
        curr = pg_conn.cursor()
        curr.execute("""SELECT id FROM users WHERE email='user1@mail.com';""")
        id = curr.fetchone()
        pg_conn.commit()
        curr.close()

    body = json.dumps({
        "user_id": id[0],
        "email": "user2@mail.com",
        "password": "P@ssw0rd2"
    })

    csrf_access = res.cookies['csrf_access_token']
    csrf_refresh = res.cookies['csrf_refresh_token']
    cookies = res.cookies
    headers = {'Content-Type': 'application/json',
               'X-CSRF-TOKEN': csrf_access,
               'X-CSRF-TOKEN-REF': csrf_refresh}
    res = requests.put(
        url=f'{test_settings.auth_api_host}/user',
        data=body,
        headers=headers,
        cookies=cookies
    )
    assert res.status_code == HTTPStatus.OK


def test_update_email_or_password_not_found():
    body = json.dumps({"email": "user2@mail.com", "password": "P@ssw0rd2"})
    headers = {'Content-Type': 'application/json'}
    res = requests.post(
        url=f'{test_settings.auth_api_host}/user/login',
        data=body,
        headers=headers
    )
    assert res.status_code == HTTPStatus.OK

    csrf_access = res.cookies['csrf_access_token']
    csrf_refresh = res.cookies['csrf_refresh_token']
    cookies = res.cookies

    headers = {'Content-Type': 'application/json',
               'X-CSRF-TOKEN': csrf_access,
               'X-CSRF-TOKEN-REF': csrf_refresh}
    body = json.dumps({
        "user_id": "2e2c309a-1111-2222-9364-6090056ad998",
        "email": "11111@mail.com",
        "password": "P@ssw0rd2"
    })

    res = requests.put(
        url=f'{test_settings.auth_api_host}/user/',
        data=body,
        headers=headers,
        cookies=cookies
    )
    assert res.status_code == HTTPStatus.NOT_FOUND


def test_update_email_or_password_conflict():
    body = json.dumps({"email": "user2@mail.com", "password": "P@ssw0rd2"})
    headers = {'Content-Type': 'application/json'}
    res = requests.post(
        url=f'{test_settings.auth_api_host}/user/login',
        data=body,
        headers=headers
    )
    assert res.status_code == HTTPStatus.OK

    with psycopg2.connect(**test_settings.dsl) as pg_conn:
        curr = pg_conn.cursor()
        curr.execute("""DELETE FROM roles WHERE name='superadmin';""")
        curr.execute("""SELECT id FROM users WHERE email='user2@mail.com';""")
        id = curr.fetchone()
        pg_conn.commit()
        curr.close()

    csrf_access = res.cookies['csrf_access_token']
    csrf_refresh = res.cookies['csrf_refresh_token']
    cookies = res.cookies
    headers = {'Content-Type': 'application/json',
               'X-CSRF-TOKEN': csrf_access,
               'X-CSRF-TOKEN-REF': csrf_refresh}
    body = json.dumps({
        "user_id": id[0],
        "email": "user2@mail.com",
        "password": "P@ssw0rd2"
    })
    res = requests.put(
        url=f'{test_settings.auth_api_host}/user/',
        data=body,
        headers=headers,
        cookies=cookies
    )
    assert res.status_code == HTTPStatus.FORBIDDEN
