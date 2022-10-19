import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import flask_login
from flask_login import UserMixin
import psycopg2
from reader import USER, PASSWORD, DATABASE, HOST
from sqlalchemy.ext.declarative import declarative_base

db = SQLAlchemy()

class User(UserMixin):
    pass
   
class Password():
    pass

def create_website():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(32)

    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)

    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS users (email VARCHAR(100) PRIMARY KEY, password CHAR(60) NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS passwords (id SERIAL PRIMARY KEY, owner VARCHAR(100) NOT NULL, name VARCHAR(100) NOT NULL, username VARCHAR(500), password VARCHAR(500), hash VARCHAR(600), url VARCHAR(500))")

    conn.commit()
    conn.close()

    @login_manager.user_loader
    def load_user(email):
        conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
        cur = conn.cursor()

        # Check to see if the email is in the database
        cur.execute("SELECT email FROM users WHERE email = %s", (email,))
        email = cur.fetchone()
        conn.close()

        if email:
            user = User()
            user.id = email[0]
            return user
        
    return app
