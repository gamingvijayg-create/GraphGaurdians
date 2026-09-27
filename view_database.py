"""
view_database.py
----------------
Terminal helper script to inspect SQLite database tables (database.db)
"""

import sys
import sqlite3
import pandas as pd
import os

# Ensure UTF-8 encoding for Windows terminal output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def view_db():
    if not os.path.exists(DB_PATH):
        print(f"[!] Database file not found at: {DB_PATH}")
        return

    print("=" * 70)
    print(f"GRAPHGUARDIANS SQLITE DATABASE INSPECTOR ({DB_PATH})")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)

    # List all tables
    tables_df = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
    print("\nTABLES IN DATABASE:")
    print(tables_df.to_string(index=False))

    # 1. Actions Table (Account Freezes)
    print("\n" + "-" * 70)
    print("1. COUNTERMEASURE ACTIONS & ACCOUNT FREEZES (TABLE: actions)")
    print("-" * 70)
    try:
        actions_df = pd.read_sql_query("SELECT * FROM actions ORDER BY id DESC LIMIT 10;", conn)
        if not actions_df.empty:
            print(actions_df.to_string(index=False))
        else:
            print("[info] No actions logged yet.")
    except Exception as e:
        print(f"Error reading actions table: {e}")

    # 2. Registered Users
    print("\n" + "-" * 70)
    print("2. REGISTERED OFFICERS & USERS (TABLE: users)")
    print("-" * 70)
    try:
        users_df = pd.read_sql_query("SELECT id, username, bank_name, officer_email, role FROM users;", conn)
        print(users_df.to_string(index=False))
    except Exception as e:
        print(f"Error reading users table: {e}")

    # 3. Logins Table
    print("\n" + "-" * 70)
    print("3. RECENT OFFICER LOGINS (TABLE: logins)")
    print("-" * 70)
    try:
        logins_df = pd.read_sql_query("SELECT * FROM logins ORDER BY id DESC LIMIT 10;", conn)
        if not logins_df.empty:
            print(logins_df.to_string(index=False))
        else:
            print("[info] No login logs yet.")
    except Exception as e:
        print(f"Error reading logins table: {e}")

    # 4. Analysis Batches Table
    print("\n" + "-" * 70)
    print("4. RECENT FRAUD ANALYSIS BATCHES (TABLE: batches)")
    print("-" * 70)
    try:
        batches_df = pd.read_sql_query("SELECT * FROM batches ORDER BY id DESC LIMIT 5;", conn)
        if not batches_df.empty:
            print(batches_df.to_string(index=False))
        else:
            print("[info] No batch runs logged yet.")
    except Exception as e:
        print(f"Error reading batches table: {e}")

    conn.close()
    print("\n" + "=" * 70)

if __name__ == "__main__":
    view_db()
