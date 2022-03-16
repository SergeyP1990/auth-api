import json
import sys
from http import HTTPStatus

import psycopg2
import pytest
import requests

sys.path.append("/usr/src/tests/")
from settings import test_settings


@pytest.fixture()
def truncate_tables():
    with psycopg2.connect(**test_settings.dsl) as pg_conn:
        curr = pg_conn.cursor()
        curr.execute("""DELETE FROM users WHERE email='user1@mail.com';""")
        curr.execute("""DELETE FROM users WHERE email='user2@mail.com';""")
        curr.execute("""DELETE FROM roles WHERE name='superadmin';""")
        curr.execute("""DELETE FROM roles WHERE name='admin';""")
        curr.execute("""DELETE FROM roles WHERE name='kill_bill_purchase';""")
        curr.execute("""DELETE FROM roles WHERE name='kill_bill_rent';""")
        pg_conn.commit()
        curr.close()


@pytest.fixture()
def grunt_user_role():
    with psycopg2.connect(**test_settings.dsl) as pg_conn:
        curr = pg_conn.cursor()
        curr.execute("""CREATE EXTENSION IF NOT EXISTS "uuid-ossp";""")
        curr.execute(
            """INSERT INTO roles VALUES (uuid_generate_v4(), now(),now(), 'superadmin');"""
        )
        curr.execute("""SELECT id FROM roles WHERE name='superadmin';""")
        role_id = curr.fetchone()
        curr.execute("""SELECT id FROM users WHERE email='user1@mail.com';""")
        user_id = curr.fetchone()
        curr.execute(
            f"""INSERT INTO user_role VALUES (uuid_generate_v4(), now(),now(),'{user_id[0]}','{role_id[0]}');"""
        )
        pg_conn.commit()
        curr.close()


@pytest.fixture()
def create_users():
    body = json.dumps({"username": "admin", "password": "admin"})
    headers = {"Content-Type": "application/json"}
    requests.post(
        url=f"{test_settings.auth_api_host}/user/register", data=body, headers=headers
    )
    body = json.dumps({"username": "user", "password": "user"})
    headers = {"Content-Type": "application/json"}
    requests.post(
        url=f"{test_settings.auth_api_host}/user/register", data=body, headers=headers
    )
    with psycopg2.connect(**test_settings.dsl) as pg_conn:
        curr = pg_conn.cursor()
        curr.execute("""CREATE EXTENSION IF NOT EXISTS "uuid-ossp";""")
        curr.execute(
            """INSERT INTO roles VALUES (uuid_generate_v4(), now(),now(), 'superadmin');"""
        )
        curr.execute("""SELECT id FROM roles WHERE name='superadmin';""")
        role_id = curr.fetchone()
        curr.execute("""SELECT id FROM users WHERE email='admin';""")
        user_id = curr.fetchone()
        curr.execute(
            f"""INSERT INTO user_role VALUES (uuid_generate_v4(), now(),now(),'{user_id[0]}','{role_id[0]}');"""
        )
        pg_conn.commit()
        curr.close()
