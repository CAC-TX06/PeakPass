import bcrypt
import psycopg2
import psycopg2
from __init__ import db, User
from reader import USER, PASSWORD, DATABASE, HOST

def hash_new_pass(password: str):
    password = (bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())).decode('utf-8')
    return password


async def add_user(email, password):  
    if not email or not password:
        return

    if len(email) > 100:
        return "Email too long"

    if len(password) > 100:
        return "Password too long"

    password = hash_new_pass(password)

    try:
        conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
        cur = conn.cursor()

        cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        conn.commit()
        conn.close()
        return True
    except psycopg2.IntegrityError:
        return False
