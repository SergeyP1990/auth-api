import time
import psycopg2
from settings import test_settings


def wait_for_postgres():
    while True:
        try:
            with psycopg2.connect(**test_settings.dsl) as pg:
                print("Database connected.")
                break
        except psycopg2.OperationalError:
            print("Database not connected. Wait 10 seconds...")
            time.sleep(10)
