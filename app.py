from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from backend.blueprints.dashboard.dashboard import home
from config import Config, TestConfig
db = SQLAlchemy()

def create_app(test_config=False):
    app = Flask(__name__)
    if test_config:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)
    db.init_app(app)

    app.register_blueprint(home, url_prefix='/home')

    @app.route('/')
    def root():
        return 'Welcome to the root URL!'

    return app

app = create_app()




migrate = Migrate(app, db)

from backend.models import *

if __name__ == '__main__':
    app.run(debug=True)
