import asyncio
from typing import List, Dict, Any
import logging

from utils.config import Config
from database.manager import DatabaseManager
from monitors.generic_monitor import GenericStoreMonitor

class MonitorManager:
    """Manages all store monitors"""
    
    def __init__(self, config: Config, db_manager: DatabaseManager):
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Use the generic monitor for all stores
        self.generic_monitor = GenericStoreMonitor(config)
        
        # Keep a reference to supported stores
        self.supported_stores = self.generic_monitor.list_supported_stores()
    
    async def check_all_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check stock for all monitored products using generic monitor"""
        stock_changes = []
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.config.max_concurrent_checks)
        
        # Check each product
        tasks = []
        for product in products:
            task = self._check_single_product(semaphore, product)
            tasks.append(task)
        
        # Wait for all checks to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect all stock changes
            for result in results:
                if isinstance(result, dict) and result:
                    stock_changes.append(result)
                elif isinstance(result, Exception):
                    self.logger.error("Error in product check: %s", result)
        
        return stock_changes

    async def _check_single_product(
        self, 
        semaphore: asyncio.Semaphore,
        product: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check a single product with rate limiting"""
        async with semaphore:
            try:
                # Add delay for rate limiting
                await asyncio.sleep(self.config.rate_limit_delay)
                
                # Use generic monitor to check stock
                stock_result = await self.generic_monitor.check_stock(
                    product['sku'], 
                    product.get('product_url')
                )
                
                # Check if stock status changed
                if stock_result['stock_status'] != product['current_stock_status']:
                    # Update database
                    await self.db_manager.update_stock_status(
                        product['id'],
                        stock_result['stock_status'],
                        stock_result['price']
                    )
                    
                    # Return change information
                    change = {
                        'sku': product['sku'],
                        'store_name': product['store_name'],
                        'product_name': product['product_name'] or stock_result['product_name'],
                        'product_url': product['product_url'] or stock_result['product_url'],
                        'old_status': product['current_stock_status'],
                        'stock_status': stock_result['stock_status'],
                        'price': stock_result['price']
                    }
                    
                    self.logger.info(
                        "Stock change detected - %s %s: %s -> %s",
                        product['store_name'], 
                        product['sku'],
                        product['current_stock_status'], 
                        stock_result['stock_status']
                    )
                    
                    return change
                
                return {}
            
            except Exception as e:
                self.logger.error("Error checking product %s: %s", product['sku'], e)
                return {}
    
    async def cleanup(self):
        """Cleanup generic monitor session"""
        await self.generic_monitor.close_session()
