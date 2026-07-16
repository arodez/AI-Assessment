import sqlite3
import os
from typing import List, Dict, Any

DATABASE_PATH = os.environ.get("DATABASE_PATH", "training_compliance.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS engineers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            team TEXT NOT NULL,
            course TEXT NOT NULL,
            course_status TEXT NOT NULL,
            deadline TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_engineers(engineers: List[Dict[str, str]]):
    """
    Saves a list of engineers, replacing any existing dataset.
    This runs inside a transaction: if any save fails, the transaction is rolled back.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN TRANSACTION")
        # Clear existing dataset to represent the "last uploaded dataset"
        cursor.execute("DELETE FROM engineers")
        
        for eng in engineers:
            cursor.execute("""
                INSERT INTO engineers (name, email, team, course, course_status, deadline)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                eng["name"],
                eng["email"],
                eng["team"],
                eng["course"],
                eng["course_status"],
                eng["deadline"]
            ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_all_engineers() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, team, course, course_status, deadline FROM engineers")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
