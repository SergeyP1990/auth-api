import time

from redis import Redis, ConnectionError

from settings import test_settings

r = Redis(
    host=test_settings.redis_host,
    port=test_settings.redis_port
)


def wait_for_redis():
    is_connected = False

    while not is_connected:
        try:
            is_connected = r.ping()
            print('Redis connected.')
        except ConnectionError:
            print('Redis not connected. Wait 10 seconds...')
            time.sleep(10)
