import bcrypt
from __init__ import db

async def hash_new_pass(password: str):
    password = (bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())).decode('utf-8')
    return password


async def add_user(email, password):    
    db.session.execute("INSERT INTO user (email, password) VALUES (%s, %s)", email, password)
    db.session.commit()
    return True

