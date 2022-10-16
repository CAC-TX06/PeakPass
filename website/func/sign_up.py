import bcrypt
import sqlite3
import hashlib
import psycopg2
import psycopg2
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

    hash512 = hashlib.sha512(password.encode('utf-8')).hexdigest()[:256]
    conn = sqlite3.connect('breached_passwords.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM breached_passwords WHERE password LIKE ?", (hash512,))
    data = cur.fetchone()
    conn.close()

    if data:
        return "Bad Password"

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
