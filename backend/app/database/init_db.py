"""
Initialize database - create all tables if they don't exist.
"""
from app.database.session import init_db

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")
