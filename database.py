import sqlite3

conn = sqlite3.connect("transactions.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime TEXT,
    amount REAL,
    old_balance REAL,
    new_balance REAL,
    result TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully")