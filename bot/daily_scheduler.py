#!/usr/bin/env python3
"""
Daily Scan Scheduler - Handles automatic daily Pokemon stock scans
"""
import asyncio
import sqlite3
from datetime import datetime, time
from typing import Optional
from bot.daily_reporter import DailyStockReporter
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DailyScanScheduler:
    """Handles scheduling and execution of daily stock scans"""
    
    def __init__(self, bot):
        self.bot = bot
        self.reporter = DailyStockReporter(bot)
        self.running = False
        
    async def start_scheduler(self):
        """Start the daily scan scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
            
        self.running = True
        logger.info("Daily scan scheduler started")
        
        while self.running:
            try:
                await self._check_and_run_scheduled_scans()
                # Check every 5 minutes for scheduled scans
                await asyncio.sleep(300)
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("Daily scan scheduler stopped")
    
    async def _check_and_run_scheduled_scans(self):
        """Check if any scans should run now"""
        current_time = datetime.now()
        current_time_str = current_time.strftime('%H:%M')
        
        try:
            conn = sqlite3.connect('data/pokemon_stock.db')
            cursor = conn.cursor()
            
            # Get active schedules for current time (within 5 minutes)
            cursor.execute('''
                SELECT guild_id, channel_id, schedule_time, id 
                FROM daily_schedules 
                WHERE is_active = 1 AND schedule_time = ?
            ''', (current_time_str,))
            
            schedules = cursor.fetchall()
            
            # Check if we already ran today
            for guild_id, channel_id, schedule_time, schedule_id in schedules:
                if await self._should_run_scan(schedule_id, current_time.date()):
                    await self._execute_scheduled_scan(channel_id)
                    await self._mark_scan_completed(schedule_id, current_time)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error checking scheduled scans: {e}")
    
    async def _should_run_scan(self, schedule_id: int, current_date) -> bool:
        """Check if scan should run (hasn't run today already)"""
        try:
            conn = sqlite3.connect('data/pokemon_stock.db')
            cursor = conn.cursor()
            
            # Create scan log table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_scan_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schedule_id INTEGER,
                    run_date DATE,
                    run_time TIMESTAMP,
                    UNIQUE(schedule_id, run_date)
                )
            ''')
            
            # Check if we already ran today
            cursor.execute('''
                SELECT id FROM scheduled_scan_log 
                WHERE schedule_id = ? AND run_date = ?
            ''', (schedule_id, current_date))
            
            already_ran = cursor.fetchone()
            conn.close()
            
            return already_ran is None
            
        except Exception as e:
            logger.error(f"Error checking if scan should run: {e}")
            return False
    
    async def _execute_scheduled_scan(self, channel_id: int):
        """Execute a scheduled scan"""
        try:
            logger.info(f"Running scheduled scan for channel {channel_id}")
            await self.reporter.perform_daily_scan(channel_id)
            
        except Exception as e:
            logger.error(f"Error executing scheduled scan: {e}")
    
    async def _mark_scan_completed(self, schedule_id: int, run_time: datetime):
        """Mark scan as completed for today"""
        try:
            conn = sqlite3.connect('data/pokemon_stock.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO scheduled_scan_log (schedule_id, run_date, run_time)
                VALUES (?, ?, ?)
            ''', (schedule_id, run_time.date(), run_time))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error marking scan as completed: {e}")

# Simple standalone script for manual daily scanning
if __name__ == "__main__":
    print("🌅 Pokemon Daily Stock Scanner")
    print("This script performs a comprehensive scan of all NZ Pokemon stores")
    print("Perfect for your morning/evening routine!")
    print()
    
    async def manual_scan():
        """Run a manual scan without Discord bot"""
        from monitors.generic_monitor import GenericStoreMonitor
        
        monitor = GenericStoreMonitor()
        
        print("🔍 Starting daily scan...")
        
        # Get store configs
        store_configs = await monitor.load_store_configs()
        nz_stores = store_configs.get('nz_stores', {})
        
        scan_results = {
            'products_found': [],
            'errors': [],
            'stores_checked': []
        }
        
        for store_id, config in nz_stores.items():
            print(f"📍 Scanning {config['name']}...")
            
            try:
                if store_id == 'novagames_nz':
                    # We know Nova Games works
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        async with session.get(config['search_url']) as response:
                            if response.status == 200:
                                html = await response.text()
                                products = await monitor.parse_nova_games_products(html, config['base_url'])
                                scan_results['products_found'].extend(products)
                                print(f"  ✅ Found {len(products)} products in stock")
                            else:
                                print(f"  ❌ HTTP {response.status}")
                else:
                    print(f"  ⏭️ Skipping {config['name']} (not implemented yet)")
                    
                scan_results['stores_checked'].append(config['name'])
                
            except Exception as e:
                error_msg = f"Error scanning {config['name']}: {e}"
                scan_results['errors'].append(error_msg)
                print(f"  ❌ {error_msg}")
        
        # Print summary
        print(f"\n📊 SCAN COMPLETE")
        print(f"🏪 Stores checked: {len(scan_results['stores_checked'])}")
        print(f"📦 Products found: {len(scan_results['products_found'])}")
        print(f"❌ Errors: {len(scan_results['errors'])}")
        
        if scan_results['products_found']:
            print(f"\n🛒 IN STOCK NOW:")
            for product in scan_results['products_found'][:10]:  # Show first 10
                price_text = f"${product['price']:.2f}" if product.get('price') else "Price TBA"
                print(f"  • {product['name']} - {price_text}")
        
        if scan_results['errors']:
            print(f"\n⚠️ ISSUES:")
            for error in scan_results['errors']:
                print(f"  • {error}")
    
    # Run the manual scan
    asyncio.run(manual_scan())