#!/usr/bin/env python3
"""
Product monitoring utilities for checking current database state.
"""
import sqlite3
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

class ProductChecker:
    """Utility class for checking monitored products in the database."""
    
    def __init__(self, db_path: str = 'data/pokemon_stock.db'):
        self.db_path = db_path
    
    def get_all_monitored_products(self, active_only: bool = True) -> List[Tuple]:
        """
        Get all monitored products from the database.
        
        Args:
            active_only: If True, only return active products
            
        Returns:
            List of tuples containing product information
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if active_only:
                query = """
                    SELECT sku, store_name, product_name, current_stock_status, 
                           product_url, added_date, last_checked
                    FROM monitored_products 
                    WHERE is_active = 1
                    ORDER BY store_name, sku
                """
            else:
                query = """
                    SELECT sku, store_name, product_name, current_stock_status, 
                           product_url, added_date, last_checked, is_active
                    FROM monitored_products 
                    ORDER BY store_name, sku
                """
            
            cursor.execute(query)
            products = cursor.fetchall()
            conn.close()
            
            return products
            
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return []
    
    def print_monitored_products(self, active_only: bool = True):
        """Print all monitored products in a readable format."""
        products = self.get_all_monitored_products(active_only)
        
        status_filter = "active" if active_only else "all"
        print(f"\n📦 Currently monitored products ({status_filter}):")
        print("=" * 60)
        
        if not products:
            print("  ❌ No products being monitored")
            return
        
        current_store = None
        for product in products:
            if active_only:
                sku, store_name, name, status, url, created, checked = product
                is_active = True
            else:
                sku, store_name, name, status, url, created, checked, is_active = product
            
            # Group by store
            if store_name != current_store:
                current_store = store_name
                print(f"\n🏪 {store_name}:")
            
            # Format product info
            name_display = name if name else "Name not found"
            status_emoji = "✅" if status == "in_stock" else "❌"
            active_indicator = "🟢" if is_active else "⚪"
            
            print(f"  {active_indicator} {status_emoji} {sku}: {name_display}")
            print(f"     Status: {status}")
            if checked:
                print(f"     Last checked: {checked}")
            print()
    
    def get_product_count_by_store(self, active_only: bool = True) -> dict:
        """Get count of monitored products by store."""
        products = self.get_all_monitored_products(active_only)
        
        store_counts = {}
        for product in products:
            store_name = product[1]  # store_name is at index 1
            store_counts[store_name] = store_counts.get(store_name, 0) + 1
        
        return store_counts
    
    def print_summary(self):
        """Print a summary of monitoring status."""
        active_products = self.get_all_monitored_products(active_only=True)
        all_products = self.get_all_monitored_products(active_only=False)
        store_counts = self.get_product_count_by_store()
        
        print("\n📊 Monitoring Summary:")
        print("=" * 30)
        print(f"Total products: {len(all_products)}")
        print(f"Active products: {len(active_products)}")
        print(f"Inactive products: {len(all_products) - len(active_products)}")
        print(f"Stores monitored: {len(store_counts)}")
        
        if store_counts:
            print("\n📈 Products per store:")
            for store, count in sorted(store_counts.items()):
                print(f"  {store}: {count} products")

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check monitored products')
    parser.add_argument('--all', action='store_true', 
                       help='Show all products including inactive ones')
    parser.add_argument('--summary', action='store_true',
                       help='Show only summary statistics')
    
    args = parser.parse_args()
    
    checker = ProductChecker()
    
    if args.summary:
        checker.print_summary()
    else:
        checker.print_monitored_products(active_only=not args.all)
        checker.print_summary()

if __name__ == "__main__":
    main()