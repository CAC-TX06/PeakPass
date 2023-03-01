import sqlite3
import flask_login
from flask import Flask
from flask_login import UserMixin
import random

class User(UserMixin):
    pass

class Password():
    pass

def create_website():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = str(random.randint(0, 10))

    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)

    conn = sqlite3.connect("data.db")
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS users (email VARCHAR(100) PRIMARY KEY, password CHAR(60) NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS passwords (id INTEGER PRIMARY KEY, owner VARCHAR(100), name TEXT NOT NULL, username TEXT, password TEXT, hash TEXT, url TEXT)")

    conn.commit()
    conn.close()

    @login_manager.user_loader
    def load_user(email):
        conn = sqlite3.connect("data.db")
        cur = conn.cursor()

        # Check to see if the email is in the database
        cur.execute("SELECT email FROM users WHERE email = ?", (email,))
        email = cur.fetchone()
        conn.close()

        if email:
            user = User()
            user.id = email[0]
            return user

    return app
