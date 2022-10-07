import bcrypt
import sqlalchemy
from __init__ import db, User

async def hash_new_pass(password: str):
    password = (bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())).decode('utf-8')
    return password


async def add_user(email, password):   
    try:
        data = User(id=email, password=password)
        db.session.add(data)
        db.session.commit() 
        return True
    except sqlalchemy.exc.IntegrityError:
        return False

