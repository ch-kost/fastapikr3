from database import get_db_connection

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
print("Database created")
