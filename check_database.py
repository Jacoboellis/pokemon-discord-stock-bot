#!/usr/bin/env python3
"""
Check database status
"""
import sqlite3
import os

def check_database():
    db_path = 'data/pokemon_stock.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file doesn't exist yet")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("Database tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_database()