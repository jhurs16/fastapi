from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

# 49fa1124f0141d7c5cc00b47ed81bda244536cfe4c9432786e8beacffb837d17
SECRET_KEY = "a98sdfh93t9ug9wsgnw0odvklnvfg891379ba640a7efe66277"
ALGORITHM = "HS256"
GUEST_TOKEN_EXPIRE_MINUTES = 300
ACCESS_TOKEN_EXPIRE_MINUTES = 300
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30
gcnAccessTokenClientExpiration = 60

# TODO: Add salt (and pepper)!
__pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    print(f"get_password_hash(plain_password): {get_password_hash(plain_password)}")
    return __pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return __pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
