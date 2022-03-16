import sys

import psycopg2
import pytest

sys.path.append('/usr/src/tests/')
from settings import test_settings


@pytest.fixture()
def truncate_table():
    with psycopg2.connect(**test_settings.dsl) as pg_conn:
        curr = pg_conn.cursor()
        curr.execute("""DELETE FROM users WHERE email='user1@mail.com';""")
        curr.execute("""DELETE FROM users WHERE email='user2@mail.com';""")
        curr.execute("""DELETE FROM roles WHERE name='superadmin';""")
        pg_conn.commit()
        curr.close()


@pytest.fixture()
def grunt_user_role():
    with psycopg2.connect(**test_settings.dsl) as pg_conn:
        curr = pg_conn.cursor()
        curr.execute("""CREATE EXTENSION IF NOT EXISTS "uuid-ossp";""")
        curr.execute("""INSERT INTO roles VALUES (uuid_generate_v4(), now(),now(), 'superadmin');""")
        curr.execute("""SELECT id FROM roles WHERE name='superadmin';""")
        role_id = curr.fetchone()
        curr.execute("""SELECT id FROM users WHERE email='user1@mail.com';""")
        user_id = curr.fetchone()
        curr.execute(f"""INSERT INTO user_role VALUES (uuid_generate_v4(), now(),now(),'{user_id[0]}','{role_id[0]}');""")
        pg_conn.commit()
        curr.close()
