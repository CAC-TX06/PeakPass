import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from reader import USER, PASSWORD, DATABASE, HOST

db = SQLAlchemy()

def create_website():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(32)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}/{DATABASE}'
    db.init_app(app)
        
    return app
