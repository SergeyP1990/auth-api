import sys
import json
import psycopg2
from http import HTTPStatus

import requests

sys.path.append('/usr/src/tests/')
from settings import test_settings


def test_create_role(truncate_tables, create_users):
    body = json.dumps({"email": "admin", "password": "admin"})
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
    body = json.dumps({"name": "admin"})
    res = requests.post(
        url=f'{test_settings.auth_api_host}/role',
        headers=headers,
        cookies=cookies,
        data=body
    )
    assert res.status_code == HTTPStatus.OK

    body = json.dumps({"email": "user", "password": "user"})
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
    body = json.dumps({"name": "kill_bill_purchase"})
    res = requests.post(
        url=f'{test_settings.auth_api_host}/role',
        headers=headers,
        cookies=cookies,
        data=body
    )
    assert res.status_code == HTTPStatus.FORBIDDEN

    body = json.dumps({"email": "admin", "password": "admin"})
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
    body = json.dumps({"name": "kill_bill_purchase"})
    res = requests.post(
        url=f'{test_settings.auth_api_host}/role',
        headers=headers,
        cookies=cookies,
        data=body
    )
    assert res.status_code == HTTPStatus.OK


def test_role_list():
    body = json.dumps({"email": "admin", "password": "admin"})
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
    res = requests.get(
        url=f'{test_settings.auth_api_host}/role',
        headers=headers,
        cookies=cookies,
        data=body
    )
    content = json.loads(res.content)
    assert content[0]['name'] == 'superadmin'
    assert res.status_code == HTTPStatus.OK


    body = json.dumps({"email": "user", "password": "user"})
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
    res = requests.get(
        url=f'{test_settings.auth_api_host}/role',
        headers=headers,
        cookies=cookies,
        data=body
    )
    assert res.status_code == HTTPStatus.FORBIDDEN


def test_role_change():
    with psycopg2.connect(**test_settings.dsl) as pg_conn:
        curr = pg_conn.cursor()
        curr.execute("""SELECT id FROM roles WHERE name='kill_bill_purchase';""")
        id = curr.fetchone()
        curr.close()

    body = json.dumps({"email": "user", "password": "user"})
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
    body = json.dumps({"name": "kill_bill_rent"})
    res = requests.put(
        url=f'{test_settings.auth_api_host}/role/{id[0]}',
        headers=headers,
        cookies=cookies,
        data=body
    )
    assert res.status_code == HTTPStatus.FORBIDDEN

    body = json.dumps({"email": "admin", "password": "admin"})
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
    body = json.dumps({"name": "kill_bill_rent"})
    res = requests.put(
        url=f'{test_settings.auth_api_host}/role/{id[0]}',
        headers=headers,
        cookies=cookies,
        data=body
    )
    assert res.status_code == HTTPStatus.OK


def test_role_delete():
    with psycopg2.connect(**test_settings.dsl) as pg_conn:
        curr = pg_conn.cursor()
        curr.execute("""SELECT id FROM roles WHERE name='kill_bill_rent';""")
        id = curr.fetchone()
        curr.close()

    body = json.dumps({"email": "user", "password": "user"})
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
    res = requests.delete(
        url=f'{test_settings.auth_api_host}/role/{id[0]}',
        headers=headers,
        cookies=cookies
    )
    assert res.status_code == HTTPStatus.FORBIDDEN

    body = json.dumps({"email": "admin", "password": "admin"})
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
    res = requests.delete(
        url=f'{test_settings.auth_api_host}/role/{id[0]}',
        headers=headers,
        cookies=cookies
    )
    assert res.status_code == HTTPStatus.OK


def test_user_role_grunted():
    with psycopg2.connect(**test_settings.dsl) as pg_conn:
        curr = pg_conn.cursor()
        curr.execute("""SELECT id FROM users WHERE email='user';""")
        user_id = curr.fetchone()
        curr.execute("""SELECT id FROM roles WHERE name='admin';""")
        role_id = curr.fetchone()
        curr.close()

    body = json.dumps({"email": "user", "password": "user"})
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
    res = requests.put(
        url=f'{test_settings.auth_api_host}/role'
            f'/user/{user_id[0]}/role/{role_id[0]}',
        headers=headers,
        cookies=cookies
    )
    assert res.status_code == HTTPStatus.FORBIDDEN


    body = json.dumps({"email": "admin", "password": "admin"})
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
    res = requests.put(
        url=f'{test_settings.auth_api_host}/role'
            f'/user/{user_id[0]}/role/{role_id[0]}',
        headers=headers,
        cookies=cookies
    )
    assert res.status_code == HTTPStatus.OK


def test_user_role_check():
    with psycopg2.connect(**test_settings.dsl) as pg_conn:
        curr = pg_conn.cursor()
        curr.execute("""SELECT id FROM users WHERE email='user';""")
        user_id = curr.fetchone()
        curr.execute("""SELECT id FROM roles WHERE name='admin';""")
        role_id = curr.fetchone()
        curr.close()

    body = json.dumps({"email": "user", "password": "user"})
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
    res = requests.get(
        url=f'{test_settings.auth_api_host}/role'
            f'/user/{user_id[0]}/role/{role_id[0]}',
        headers=headers,
        cookies=cookies
    )
    assert res.status_code == HTTPStatus.OK


def test_user_role_delete():
    with psycopg2.connect(**test_settings.dsl) as pg_conn:
        curr = pg_conn.cursor()
        curr.execute("""SELECT id FROM users WHERE email='user';""")
        user_id = curr.fetchone()
        curr.execute("""SELECT id FROM roles WHERE name='admin';""")
        role_id = curr.fetchone()
        curr.close()

    body = json.dumps({"email": "admin", "password": "admin"})
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
    res = requests.delete(
        url=f'{test_settings.auth_api_host}/role'
            f'/user/{user_id[0]}/role/{role_id[0]}',
        headers=headers,
        cookies=cookies
    )
    assert res.status_code == HTTPStatus.OK
