import bcrypt
from fastapi import HTTPException


def hash_password(password: str) -> str:
    password = password.encode()
    password_hash = bcrypt.hashpw(password, bcrypt.gensalt())
    return password_hash.decode()

def check_password(password: str, password_hashed: str) -> bool:
    password = password.encode()
    password_hashed = password_hashed.encode()
    return bcrypt.checkpw(password, password_hashed)

def check_permissions(user, user_id):
    if user.role != "admin" and user_id != user.id:
        raise HTTPException(403, "Insufficient privileges")