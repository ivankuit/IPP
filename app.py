from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import  render_template

from backend.blueprints.home_page.home_page import page_bp
from config import Config, TestConfig
from manage import register_commands
from database import db

def create_app(test_config=False):
    app = Flask(__name__)
    if test_config:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)
    db.init_app(app)

    app.register_blueprint(page_bp)


    @app.route('/')
    def root():
        return render_template('index.html')

    register_commands(app)

    return app

app = create_app()




migrate = Migrate(app, db)

from backend.models import *

if __name__ == '__main__':
    app.run(debug=True)
