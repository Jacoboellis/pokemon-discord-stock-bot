import aiosqlite
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from utils.logger import setup_logger

class DatabaseManager:
    """Manages SQLite database operations for the Pokemon Stock Bot"""
    
    def __init__(self, db_path: str = "data/pokemon_stock.db"):
        self.db_path = db_path
        self.logger = setup_logger(__name__)
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    async def initialize(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS monitored_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sku TEXT NOT NULL,
                    store_name TEXT NOT NULL,
                    product_name TEXT,
                    product_url TEXT,
                    current_stock_status TEXT DEFAULT 'Unknown',
                    last_price REAL,
                    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    UNIQUE(sku, store_name)
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS stock_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    stock_status TEXT NOT NULL,
                    price REAL,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES monitored_products (id)
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    notification_enabled BOOLEAN DEFAULT 1,
                    preferred_stores TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS upcoming_releases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_name TEXT NOT NULL,
                    release_date DATE NOT NULL,
                    estimated_price REAL,
                    store_name TEXT,
                    description TEXT,
                    image_url TEXT,
                    advance_notification_sent BOOLEAN DEFAULT 0,
                    release_day_notification_sent BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS community_sightings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    user_name TEXT,
                    product_name TEXT NOT NULL,
                    store_name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    stock_count TEXT,
                    price REAL,
                    image_url TEXT,
                    is_verified BOOLEAN DEFAULT 0,
                    verified_by TEXT,
                    verification_notes TEXT,
                    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await db.commit()
            self.logger.info("Database initialized successfully")
    
    async def add_product(self, sku: str, store_name: str, product_name: str = None, product_url: str = None) -> bool:
        """Add a product to monitor"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR REPLACE INTO monitored_products 
                    (sku, store_name, product_name, product_url)
                    VALUES (?, ?, ?, ?)
                ''', (sku, store_name, product_name, product_url))
                await db.commit()
                self.logger.info(f"Added product {sku} from {store_name}")
                return True
        except Exception as e:
            self.logger.error(f"Error adding product: {e}")
            return False
    
    async def remove_product(self, sku: str, store_name: str = None) -> bool:
        """Remove a product from monitoring"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if store_name:
                    await db.execute(
                        'DELETE FROM monitored_products WHERE sku = ? AND store_name = ?',
                        (sku, store_name)
                    )
                else:
                    await db.execute('DELETE FROM monitored_products WHERE sku = ?', (sku,))
                await db.commit()
                self.logger.info(f"Removed product {sku}")
                return True
        except Exception as e:
            self.logger.error(f"Error removing product: {e}")
            return False
    
    async def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all monitored products"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT * FROM monitored_products WHERE is_active = 1'
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Error getting products: {e}")
            return []
    
    async def update_stock_status(self, product_id: int, stock_status: str, price: float = None) -> bool:
        """Update product stock status and add to history"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Update product
                await db.execute('''
                    UPDATE monitored_products 
                    SET current_stock_status = ?, last_price = ?, last_checked = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (stock_status, price, product_id))
                
                # Add to history
                await db.execute('''
                    INSERT INTO stock_history (product_id, stock_status, price)
                    VALUES (?, ?, ?)
                ''', (product_id, stock_status, price))
                
                await db.commit()
                return True
        except Exception as e:
            self.logger.error(f"Error updating stock status: {e}")
            return False
    
    async def get_stock_changes(self, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get recent stock changes within specified minutes"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT mp.sku, mp.store_name, mp.product_name, mp.product_url,
                           sh.stock_status, sh.price, sh.checked_at
                    FROM stock_history sh
                    JOIN monitored_products mp ON sh.product_id = mp.id
                    WHERE sh.checked_at >= datetime('now', '-{} minutes')
                    ORDER BY sh.checked_at DESC
                '''.format(minutes)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Error getting stock changes: {e}")
            return []
    
    def close(self):
        """Close database connections"""
        # aiosqlite connections are closed automatically
        self.logger.info("Database connections closed")
    
    # Upcoming Releases Methods
    async def add_upcoming_release(self, product_name: str, release_date: str, estimated_price: float = None, 
                                 store_name: str = None, description: str = None) -> bool:
        """Add an upcoming release"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO upcoming_releases 
                    (product_name, release_date, estimated_price, store_name, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (product_name, release_date, estimated_price, store_name, description))
                await db.commit()
                self.logger.info(f"Added upcoming release: {product_name}")
                return True
        except Exception as e:
            self.logger.error(f"Error adding upcoming release: {e}")
            return False
    
    async def get_releases_for_advance_notification(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get releases that need advance notification (within X days and not yet notified)"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT * FROM upcoming_releases 
                    WHERE release_date <= date('now', '+{} days')
                    AND advance_notification_sent = 0
                    ORDER BY release_date ASC
                '''.format(days_ahead)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Error getting releases for advance notification: {e}")
            return []
    
    async def get_releases_for_today(self) -> List[Dict[str, Any]]:
        """Get releases happening today that need release day notification"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT * FROM upcoming_releases 
                    WHERE release_date = date('now')
                    AND release_day_notification_sent = 0
                    ORDER BY release_date ASC
                ''') as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Error getting releases for today: {e}")
            return []
    
    async def mark_advance_notification_sent(self, release_id: int) -> bool:
        """Mark advance notification as sent"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'UPDATE upcoming_releases SET advance_notification_sent = 1 WHERE id = ?',
                    (release_id,)
                )
                await db.commit()
                return True
        except Exception as e:
            self.logger.error(f"Error marking advance notification sent: {e}")
            return False
    
    async def mark_release_day_notification_sent(self, release_id: int) -> bool:
        """Mark release day notification as sent"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'UPDATE upcoming_releases SET release_day_notification_sent = 1 WHERE id = ?',
                    (release_id,)
                )
                await db.commit()
                return True
        except Exception as e:
            self.logger.error(f"Error marking release day notification sent: {e}")
            return False
    
    # Community Sightings Methods
    async def add_community_sighting(self, user_id: str, user_name: str, product_name: str, 
                                   store_name: str, location: str, stock_count: str = None, 
                                   price: float = None, image_url: str = None) -> int:
        """Add a community sighting and return the sighting ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute('''
                    INSERT INTO community_sightings 
                    (user_id, user_name, product_name, store_name, location, stock_count, price, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, user_name, product_name, store_name, location, stock_count, price, image_url))
                await db.commit()
                sighting_id = cursor.lastrowid
                self.logger.info(f"Added community sighting: {sighting_id}")
                return sighting_id
        except Exception as e:
            self.logger.error(f"Error adding community sighting: {e}")
            return 0
    
    async def verify_sighting(self, sighting_id: int, verified_by: str, notes: str = None) -> bool:
        """Verify a community sighting"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE community_sightings 
                    SET is_verified = 1, verified_by = ?, verification_notes = ?
                    WHERE id = ?
                ''', (verified_by, notes, sighting_id))
                await db.commit()
                return True
        except Exception as e:
            self.logger.error(f"Error verifying sighting: {e}")
            return False
    
    async def get_unverified_sightings(self) -> List[Dict[str, Any]]:
        """Get all unverified community sightings"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT * FROM community_sightings 
                    WHERE is_verified = 0
                    ORDER BY reported_at DESC
                ''') as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Error getting unverified sightings: {e}")
            return []
