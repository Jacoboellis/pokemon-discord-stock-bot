#!/usr/bin/env python3
"""
Daily Stock Report System
Provides comprehensive daily stock summaries and scanning functionality
"""
import asyncio
import aiohttp
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import discord
from discord.ext import commands
from monitors.generic_monitor import GenericStoreMonitor
from database.manager import DatabaseManager
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DailyStockReporter:
    """Handles daily stock reporting and scanning operations"""
    
    def __init__(self, bot):
        self.bot = bot
        self.monitor = GenericStoreMonitor(bot.config)
        self.db_manager = DatabaseManager()
        
    async def perform_daily_scan(self, report_channel_id: int = None) -> Dict:
        """
        Performs a comprehensive daily scan of all NZ stores
        Returns summary of findings
        """
        logger.info("Starting daily stock scan...")
        
        scan_results = {
            'timestamp': datetime.now(),
            'stores_scanned': [],
            'products_found': [],
            'errors': [],
            'new_arrivals': [],
            'stock_changes': []
        }
        
        # Get all NZ stores from config
        store_configs = self.monitor.load_store_configs()
        nz_stores = store_configs
        
        for store_id, config in nz_stores.items():
            try:
                logger.info(f"Scanning {config['name']}...")
                
                # Perform store scan
                store_results = await self._scan_store(store_id, config)
                scan_results['stores_scanned'].append({
                    'store_id': store_id,
                    'store_name': config['name'],
                    'status': store_results['status'],
                    'products_found': len(store_results.get('products', [])),
                    'error': store_results.get('error')
                })
                
                # Add products to results
                if store_results.get('products'):
                    for product in store_results['products']:
                        product['store_id'] = store_id
                        product['store_name'] = config['name']
                        scan_results['products_found'].append(product)
                        
                        # Check if this is a new arrival (not in database)
                        if await self._is_new_arrival(product):
                            scan_results['new_arrivals'].append(product)
                
            except Exception as e:
                error_msg = f"Error scanning {config['name']}: {str(e)}"
                logger.error(error_msg)
                scan_results['errors'].append(error_msg)
        
        # Save scan results to database
        await self._save_scan_results(scan_results)
        
        # Send report if channel specified
        if report_channel_id:
            await self._send_daily_report(report_channel_id, scan_results)
        
        logger.info(f"Daily scan complete. Found {len(scan_results['products_found'])} products across {len(scan_results['stores_scanned'])} stores")
        return scan_results
    
    async def _scan_store(self, store_id: str, config: Dict) -> Dict:
        """Scan a single store for Pokemon products"""
        try:
            if store_id == 'novagames_nz':
                # Nova Games - we know this works
                products = await self._scan_nova_games(config)
                return {'status': 'success', 'products': products}
                
            elif store_id == 'thewarehouse_nz':
                # Try The Warehouse
                products = await self._scan_warehouse_nz(config)
                return {'status': 'success', 'products': products}
                
            elif store_id == 'jbhifi_nz':
                # Try JB Hi-Fi
                products = await self._scan_jbhifi_nz(config)
                return {'status': 'success', 'products': products}
                
            else:
                # For other stores, try generic approach
                return {'status': 'skipped', 'error': 'Store scanning not implemented yet'}
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def _scan_nova_games(self, config: Dict) -> List[Dict]:
        """Scan Nova Games NZ - we know this works perfectly"""
        products = []
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(config['search_url']) as response:
                    if response.status == 200:
                        html = await response.text()
                        # Parse Nova Games products
                        products = await self.monitor.parse_nova_games_products(html, config['base_url'])
            except Exception as e:
                logger.error(f"Error scanning Nova Games: {e}")
        
        return products
    
    async def _scan_warehouse_nz(self, config: Dict) -> List[Dict]:
        """Scan The Warehouse NZ for Pokemon products"""
        products = []
        search_url = config['search_url'].replace('{query}', 'pokemon+tcg')
        
        async with aiohttp.ClientSession() as session:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                async with session.get(search_url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        # Parse Warehouse products (would need implementation)
                        logger.info(f"The Warehouse scan successful - got {len(html)} chars")
                    else:
                        logger.warning(f"The Warehouse returned status {response.status}")
            except Exception as e:
                logger.error(f"Error scanning The Warehouse: {e}")
        
        return products
    
    async def _scan_jbhifi_nz(self, config: Dict) -> List[Dict]:
        """Scan JB Hi-Fi NZ for Pokemon products"""
        products = []
        search_url = config['search_url'].replace('{query}', 'pokemon%20tcg')
        
        async with aiohttp.ClientSession() as session:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                async with session.get(search_url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        # Parse JB Hi-Fi products (would need implementation)
                        logger.info(f"JB Hi-Fi scan successful - got {len(html)} chars")
                    else:
                        logger.warning(f"JB Hi-Fi returned status {response.status}")
            except Exception as e:
                logger.error(f"Error scanning JB Hi-Fi: {e}")
        
        return products
    
    async def _is_new_arrival(self, product: Dict) -> bool:
        """Check if product is a new arrival (not in database)"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check if product exists in database
                conn = sqlite3.connect('data/pokemon_stock.db')
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT id FROM monitored_products WHERE sku = ? AND store_name LIKE ?",
                    (product.get('sku', ''), f"%{product.get('store_id', '')}%")
                )
                exists = cursor.fetchone()
                conn.close()
                
                return exists is None
        except Exception as e:
            logger.error(f"Error checking if product is new arrival: {e}")
            return False
    
    async def _save_scan_results(self, results: Dict):
        """Save scan results to database for historical tracking"""
        try:
            conn = sqlite3.connect('data/pokemon_stock.db')
            cursor = conn.cursor()
            
            # Create daily_scans table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_date DATE NOT NULL,
                    scan_time TIMESTAMP NOT NULL,
                    stores_scanned INTEGER,
                    products_found INTEGER,
                    new_arrivals INTEGER,
                    errors TEXT,
                    summary TEXT
                )
            ''')
            
            # Insert scan summary
            cursor.execute('''
                INSERT INTO daily_scans (scan_date, scan_time, stores_scanned, products_found, new_arrivals, errors, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                results['timestamp'].date(),
                results['timestamp'],
                len(results['stores_scanned']),
                len(results['products_found']),
                len(results['new_arrivals']),
                '; '.join(results['errors']) if results['errors'] else None,
                f"Scanned {len(results['stores_scanned'])} stores, found {len(results['products_found'])} products"
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving scan results: {e}")
    
    async def _send_daily_report(self, channel_id: int, results: Dict):
        """Send formatted daily report to Discord channel"""
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"Could not find channel {channel_id}")
                return
            
            # Create embed report
            embed = discord.Embed(
                title="🌅 Daily Pokemon Stock Report",
                description=f"Scan completed at {results['timestamp'].strftime('%I:%M %p')}",
                color=0x3498db
            )
            
            # Stores scanned summary
            stores_summary = []
            for store in results['stores_scanned']:
                status_emoji = "✅" if store['status'] == 'success' else "❌" if store['status'] == 'error' else "⏭️"
                stores_summary.append(f"{status_emoji} **{store['store_name']}**: {store['products_found']} products")
            
            embed.add_field(
                name="🏪 Stores Scanned",
                value="\n".join(stores_summary) if stores_summary else "No stores scanned",
                inline=False
            )
            
            # New arrivals
            if results['new_arrivals']:
                arrivals_text = []
                for product in results['new_arrivals'][:5]:  # Show first 5
                    price_text = f"${product['price']:.2f}" if product.get('price') else "Price TBA"
                    arrivals_text.append(f"• **{product['name']}** - {price_text}\n  📍 {product['store_name']}")
                
                embed.add_field(
                    name="🆕 New Arrivals Today",
                    value="\n".join(arrivals_text),
                    inline=False
                )
            else:
                embed.add_field(
                    name="🆕 New Arrivals Today",
                    value="No new arrivals detected",
                    inline=False
                )
            
            # Summary stats
            total_products = len(results['products_found'])
            working_stores = len([s for s in results['stores_scanned'] if s['status'] == 'success'])
            
            embed.add_field(
                name="📊 Summary",
                value=f"**{total_products}** products found\n**{working_stores}** stores working\n**{len(results['new_arrivals'])}** new arrivals",
                inline=True
            )
            
            # Errors if any
            if results['errors']:
                embed.add_field(
                    name="⚠️ Issues",
                    value="\n".join(results['errors'][:3]),  # Show first 3 errors
                    inline=True
                )
            
            embed.set_footer(text="💡 Use /daily_scan to run manual scan • Report sightings with /report_sighting")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending daily report: {e}")
    
    async def get_stock_summary(self) -> Dict:
        """Get current stock summary across all monitored stores"""
        try:
            conn = sqlite3.connect('data/pokemon_stock.db')
            cursor = conn.cursor()
            
            # Get monitored products with recent stock status
            cursor.execute('''
                SELECT store_name, sku, product_name, current_stock_status, last_price, last_checked
                FROM monitored_products 
                WHERE is_active = 1
                ORDER BY last_checked DESC
            ''')
            
            products = cursor.fetchall()
            
            # Get community sightings from today
            cursor.execute('''
                SELECT store_name, product_name, price, reported_by, reported_at
                FROM community_sightings 
                WHERE DATE(reported_at) = DATE('now')
                ORDER BY reported_at DESC
            ''')
            
            sightings = cursor.fetchall()
            
            conn.close()
            
            return {
                'monitored_products': products,
                'community_sightings': sightings,
                'total_monitored': len(products),
                'todays_sightings': len(sightings)
            }
            
        except Exception as e:
            logger.error(f"Error getting stock summary: {e}")
            return {}