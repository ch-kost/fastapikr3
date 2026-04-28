import secrets
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI()
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fake_users_db = {}


class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str


def get_user(username: str):
    for stored_username, user in fake_users_db.items():
        if secrets.compare_digest(stored_username, username):
            return user
    return None


def auth_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = get_user(credentials.username)
    if user is None or not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


@app.post("/register")
def register(user: User):
    if get_user(user.username) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    hashed_password = pwd_context.hash(user.password)
    fake_users_db[user.username] = UserInDB(username=user.username, hashed_password=hashed_password)
    return {"message": "User successfully registered"}


@app.get("/login")
def login(user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {user.username}!"}
