from utils.wait_for_postgres import wait_for_postgres
from utils.wait_for_redis import wait_for_redis


if __name__ == "__main__":
    wait_for_postgres()
    wait_for_redis()
