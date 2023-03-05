import bcrypt
import sqlite3

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
        conn = sqlite3.connect("data.db")
        cur = conn.cursor()

        cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
