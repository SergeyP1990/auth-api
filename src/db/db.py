from core.config import settings
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

postgres_uri = f'postgresql+psycopg2://' \
               f'{settings.postgres_user}:' \
               f'{settings.postgres_password}@' \
               f'{settings.postgres_host}/' \
               f'{settings.postgres_database_name}'

db = SQLAlchemy()


def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = postgres_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
