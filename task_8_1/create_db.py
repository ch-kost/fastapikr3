from database import get_db_connection

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
print("Database created")
