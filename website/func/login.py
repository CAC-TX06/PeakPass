import bcrypt
from __init__ import User

async def correct_login_information(email: str, password: str):
    user = User.query.filter_by(id=email).first()
    if user:
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return True
    return False
