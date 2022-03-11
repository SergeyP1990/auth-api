from flask import Flask
from db.db import init_db, db
from db.models import User


def create_app():
    app = Flask(__name__)
    init_db(app)
    init_db(app)
    app.app_context().push()
    db.create_all()
    return app


app = create_app()


#Тестовая функция
@app.route('/')
def index():
    #admin = User(email='aa1@mail.ru', password='password', full_name='admin1', phone_number='79234567643')
    #db.session.add(admin)
    #db.session.commit()
    return 'index page'

