# Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement.

"""
Initialize database - create all tables if they don't exist.
"""
from app.database.session import init_db

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")
