import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager
from reader import USER, PASSWORD, DATABASE, HOST

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.String(100), unique=True, primary_key=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)

class Password(db.Model):
    id = db.Column(db.String(500), unique=True, primary_key=True, nullable=False) # Name
    owner = db.Column(db.String(100), nullable=True) # Email of the owner
    username = db.Column(db.String(100), unique=False, nullable=True) # Username
    password = db.Column(db.String(500), nullable=True)
    url = db.Column(db.String(5000), nullable=True)


def create_website():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(32)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}/{DATABASE}'
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)
        
    return app
