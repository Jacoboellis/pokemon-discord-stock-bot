#!/usr/bin/env python3
"""Update database schema for dual notification system"""

import sqlite3
import os

def update_schema():
    db_path = 'data/pokemon_stock.db'
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get current table schema
        cursor.execute('PRAGMA table_info(upcoming_releases)')
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f'Current columns: {column_names}')
        
        # Check if new columns exist
        needs_update = False
        if 'advance_notification_sent' not in column_names:
            print('Adding advance_notification_sent column...')
            cursor.execute('ALTER TABLE upcoming_releases ADD COLUMN advance_notification_sent BOOLEAN DEFAULT FALSE')
            needs_update = True
            
        if 'release_day_notification_sent' not in column_names:
            print('Adding release_day_notification_sent column...')
            cursor.execute('ALTER TABLE upcoming_releases ADD COLUMN release_day_notification_sent BOOLEAN DEFAULT FALSE')
            needs_update = True
        
        # If we have the old notification_sent column, we need to recreate the table
        if 'notification_sent' in column_names:
            print('Recreating table to remove old notification_sent column...')
            
            # Create new table
            cursor.execute('''
                CREATE TABLE upcoming_releases_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_name TEXT NOT NULL,
                    release_date DATE NOT NULL,
                    estimated_price REAL,
                    store_name TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    advance_notification_sent BOOLEAN DEFAULT FALSE,
                    release_day_notification_sent BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Copy data from old table
            cursor.execute('''
                INSERT INTO upcoming_releases_new 
                (id, product_name, release_date, estimated_price, store_name, description, created_at)
                SELECT id, product_name, release_date, estimated_price, store_name, description, created_at
                FROM upcoming_releases
            ''')
            
            # Drop old table and rename new one
            cursor.execute('DROP TABLE upcoming_releases')
            cursor.execute('ALTER TABLE upcoming_releases_new RENAME TO upcoming_releases')
            needs_update = True
        
        if needs_update:
            conn.commit()
            print('Schema update completed successfully!')
        else:
            print('Schema is already up to date.')
            
        # Show final schema
        cursor.execute('PRAGMA table_info(upcoming_releases)')
        final_columns = cursor.fetchall()
        print(f'Final columns: {[col[1] for col in final_columns]}')
        
    except Exception as e:
        print(f'Error updating schema: {e}')
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    update_schema()