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
        pg_conn.commit()
        curr.close()
