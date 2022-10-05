import os 
import hashlib
import hmac
import asyncpg
from reader import USER, PASSWORD, DATABASE, HOST

async def correct_login_information(email: str, password: str):
    conn = await asyncpg.connect(user=USER, password=PASSWORD, database=DATABASE, host=HOST)
    login_data = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
    if login_data:
        salt = login_data["salt"]
        print(salt)
        key = login_data["key"]
        print(key)
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return hmac.compare_digest(key, new_key)