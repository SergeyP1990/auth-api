import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from core.config import settings

postgres_uri = (
    f"postgresql+psycopg2://"
    f"{settings.postgres_user}:"
    f"{settings.postgres_password}@"
    f"{settings.postgres_host}/"
    f"{settings.postgres_database_name}"
)

db = SQLAlchemy()
redis_db_acc_tok = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

redis_db_ref_tok = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=1)


def init_db(app: Flask):
    app.config["SQLALCHEMY_DATABASE_URI"] = postgres_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
