import bcrypt
import sqlite3

async def correct_login_information(email: str, password: str):
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()

    cur.execute("SELECT password FROM users WHERE email = ?", (email,))
    hashed_password = cur.fetchone()
    conn.close()

    if hashed_password:
        if bcrypt.checkpw(password.encode('utf-8'), str(hashed_password[0]).encode('utf-8')):
            return True
    return False
