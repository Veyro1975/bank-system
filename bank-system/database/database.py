import sqlite3

class Database:
    def __init__(self, db_name="bank.db"):
        self.db_name = db_name
        self.create_tables()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    account_number TEXT PRIMARY KEY,
                    full_name TEXT,
                    pin_hash TEXT,
                    balance INTEGER DEFAULT 0
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_number TEXT,
                    type TEXT,
                    amount INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
