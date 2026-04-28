import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional
import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
fake_users_db = {}
resources = {}
roles_permissions = {
    "admin": {"create", "read", "update", "delete"},
    "user": {"read", "update"},
    "guest": {"read"},
}


class RegisterData(BaseModel):
    username: str
    password: str
    role: Literal["admin", "user", "guest"] = "user"


class LoginData(BaseModel):
    username: str
    password: str


class UserInDB(BaseModel):
    username: str
    hashed_password: str
    role: str


class ResourceData(BaseModel):
    title: str
    description: str


def get_user(username: str):
    for stored_username, user in fake_users_db.items():
        if secrets.compare_digest(stored_username, username):
            return user
    return None


def create_access_token(user: UserInDB) -> str:
    payload = {
        "sub": user.username,
        "role": user.role,
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


def require_permission(permission: str):
    def dependency(user: UserInDB = Depends(get_current_user)):
        if permission not in roles_permissions.get(user.role, set()):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return user
    return dependency


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterData):
    if get_user(data.username) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    fake_users_db[data.username] = UserInDB(username=data.username, hashed_password=pwd_context.hash(data.password), role=data.role)
    return {"message": "New user created", "role": data.role}


@app.post("/login")
def login(data: LoginData):
    user = get_user(data.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed")
    return {"access_token": create_access_token(user), "token_type": "bearer"}


@app.get("/protected_resource")
def protected_resource(user: UserInDB = Depends(require_permission("read"))):
    return {"message": "Access granted", "role": user.role}


@app.post("/admin/resource")
def create_resource(data: ResourceData, user: UserInDB = Depends(require_permission("create"))):
    resource_id = len(resources) + 1
    resources[resource_id] = {"id": resource_id, "title": data.title, "description": data.description}
    return resources[resource_id]


@app.get("/guest/resource")
def read_public_resource(user: UserInDB = Depends(require_permission("read"))):
    return {"message": "Read access granted", "resources": list(resources.values())}


@app.put("/user/resource/{resource_id}")
def update_resource(resource_id: int, data: ResourceData, user: UserInDB = Depends(require_permission("update"))):
    if resource_id not in resources:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    resources[resource_id] = {"id": resource_id, "title": data.title, "description": data.description}
    return resources[resource_id]


@app.delete("/admin/resource/{resource_id}")
def delete_resource(resource_id: int, user: UserInDB = Depends(require_permission("delete"))):
    if resource_id not in resources:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    del resources[resource_id]
    return {"message": "Resource deleted"}
