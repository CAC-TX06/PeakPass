import os
import psycopg2
import flask_login
from flask import Flask
from flask_login import UserMixin
from reader import CONNECTION_STRING

class User(UserMixin):
    pass
   
class Password():
    pass

def create_website():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(32)

    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)

    conn = psycopg2.connect(CONNECTION_STRING)
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS users (email VARCHAR(100) PRIMARY KEY, password CHAR(60) NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS passwords (id SERIAL PRIMARY KEY, owner VARCHAR(100), name TEXT NOT NULL, username TEXT, password TEXT, hash TEXT, url TEXT)")
    
    conn.commit()
    conn.close()

    @login_manager.user_loader
    def load_user(email):
        conn = psycopg2.connect(CONNECTION_STRING)
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
