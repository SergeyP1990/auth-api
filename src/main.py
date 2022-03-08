from flask import Flask

from db.db import init_db, db

app = Flask(__name__)


def main():
    init_db(app)
    app.app_context().push()
    db.create_all()
    app.run(debug=True)


@app.route('/')
def index():
    return 'Index Page'


if __name__ == '__main__':
    main()
