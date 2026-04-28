from fastapi import FastAPI
from pydantic import BaseModel
try:
    from .database import get_db_connection
except ImportError:
    from database import get_db_connection

app = FastAPI()


class User(BaseModel):
    username: str
    password: str


def init_db():
    connection = get_db_connection()
    connection.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
    """)
    connection.commit()
    connection.close()


@app.on_event("startup")
def startup():
    init_db()


@app.post("/register")
def register(user: User):
    connection = get_db_connection()
    connection.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, user.password))
    connection.commit()
    connection.close()
    return {"message": "User registered successfully!"}
