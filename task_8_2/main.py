from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
try:
    from .database import get_db_connection
except ImportError:
    from database import get_db_connection

app = FastAPI()


class TodoCreate(BaseModel):
    title: str
    description: str


class TodoUpdate(BaseModel):
    title: str
    description: str
    completed: bool


def init_db():
    connection = get_db_connection()
    connection.execute("""
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        completed INTEGER NOT NULL DEFAULT 0
    )
    """)
    connection.commit()
    connection.close()


def row_to_todo(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "completed": bool(row["completed"]),
    }


@app.on_event("startup")
def startup():
    init_db()


@app.post("/todos", status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate):
    connection = get_db_connection()
    cursor = connection.execute(
        "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
        (todo.title, todo.description, 0),
    )
    connection.commit()
    todo_id = cursor.lastrowid
    row = connection.execute("SELECT id, title, description, completed FROM todos WHERE id = ?", (todo_id,)).fetchone()
    connection.close()
    return row_to_todo(row)


@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    connection = get_db_connection()
    row = connection.execute("SELECT id, title, description, completed FROM todos WHERE id = ?", (todo_id,)).fetchone()
    connection.close()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return row_to_todo(row)


@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate):
    connection = get_db_connection()
    row = connection.execute("SELECT id FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if row is None:
        connection.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    connection.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (todo.title, todo.description, int(todo.completed), todo_id),
    )
    connection.commit()
    updated = connection.execute("SELECT id, title, description, completed FROM todos WHERE id = ?", (todo_id,)).fetchone()
    connection.close()
    return row_to_todo(updated)


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    connection = get_db_connection()
    row = connection.execute("SELECT id FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if row is None:
        connection.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    connection.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    connection.commit()
    connection.close()
    return {"message": "Todo deleted successfully"}
