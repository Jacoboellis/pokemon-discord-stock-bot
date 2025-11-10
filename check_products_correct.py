#!/usr/bin/env python3
"""
Check what products are currently being monitored
"""
import sqlite3

def check_monitored_products():
    try:
        conn = sqlite3.connect('data/pokemon_stock.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT sku, store_name, product_name, current_stock_status FROM monitored_products WHERE is_active = 1")
        products = cursor.fetchall()
        
        print("Currently monitored products:")
        if products:
            for sku, store_name, name, status in products:
                print(f"  {store_name}: {sku} - {name or 'Name not found'} ({status})")
        else:
            print("  No active products being monitored")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_monitored_products()