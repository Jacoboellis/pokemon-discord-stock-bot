#!/usr/bin/env python3
"""
Check what products are currently being monitored
"""
import sqlite3

def check_monitored_products():
    try:
        conn = sqlite3.connect('data/pokemon_stock.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT store, sku, url, product_name FROM monitored_products")
        products = cursor.fetchall()
        
        print("Currently monitored products:")
        if products:
            for store, sku, url, name in products:
                print(f"  {store}: {sku} - {name}")
        else:
            print("  No products being monitored yet")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_monitored_products()