#!/usr/bin/env python3
"""
Check database schema
"""
import sqlite3

def check_schema():
    try:
        conn = sqlite3.connect('data/pokemon_stock.db')
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(monitored_products)")
        columns = cursor.fetchall()
        
        print("monitored_products table schema:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")  # name (type)
        
        # Check current data
        cursor.execute("SELECT * FROM monitored_products")
        products = cursor.fetchall()
        
        print(f"\nRows in monitored_products: {len(products)}")
        if products:
            print("Sample data:")
            for product in products[:3]:  # Show first 3
                print(f"  {product}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_schema()