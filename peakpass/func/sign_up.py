import os
import hashlib
import asyncpg
from typing import Tuple
from reader import USER, PASSWORD, DATABASE, HOST

async def hash_new_pass(password: str) -> Tuple[bytes, bytes]:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt, key


async def add_user(email, info):
    conn = await asyncpg.connect(user=USER, password=PASSWORD, database=DATABASE, host=HOST)

    try:
        await conn.execute("INSERT INTO users (email, key, salt) VALUES ($1, $2, $3)", email, info[1], info[0])
        return True
    except asyncpg.exceptions.UniqueViolationError:
        return False