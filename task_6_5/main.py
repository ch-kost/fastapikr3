import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
fake_users_db = {}
rate_storage = {}


class User(BaseModel):
    username: str
    password: str


class UserInDB(BaseModel):
    username: str
    hashed_password: str


def rate_limit(name: str, limit: int, seconds: int):
    def dependency(request: Request):
        client = request.client.host if request.client else "unknown"
        window = int(time.time()) // seconds
        key = f"{name}:{client}:{window}"
        rate_storage[key] = rate_storage.get(key, 0) + 1
        for stored_key in list(rate_storage.keys()):
            try:
                stored_window = int(stored_key.rsplit(":", 1)[1])
                if stored_window < window - 1:
                    del rate_storage[stored_key]
            except ValueError:
                pass
        if rate_storage[key] > limit:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")
    return dependency


def get_user(username: str):
    for stored_username, user in fake_users_db.items():
        if secrets.compare_digest(stored_username, username):
            return user
    return None


def create_access_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(authorization: Optional[str] = Header(default=None, alias="Authorization")):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = get_user(username)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@app.post("/register", status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit("register", 1, 60))])
def register(user: User):
    if get_user(user.username) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    fake_users_db[user.username] = UserInDB(username=user.username, hashed_password=pwd_context.hash(user.password))
    return {"message": "New user created"}


@app.post("/login", dependencies=[Depends(rate_limit("login", 5, 60))])
def login(user: User):
    db_user = get_user(user.username)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed")
    return {"access_token": create_access_token(db_user.username), "token_type": "bearer"}


@app.get("/protected_resource")
def protected_resource(user: UserInDB = Depends(get_current_user)):
    return {"message": "Access granted"}
