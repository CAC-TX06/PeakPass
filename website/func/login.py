import bcrypt
from __init__ import db 
from flask_sqlalchemy import SQLAlchemy
from reader import USER, PASSWORD, DATABASE, HOST

async def correct_login_information(email: str, password: str):
    login_data = db.session.execute("SELECT email, password FROM user WHERE email = %s", email).fetchone()
    if login_data:
        bcrypt.checkpw(password.encode('utf-8'), login_data[0])
    else:
        return False