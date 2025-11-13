#!/usr/bin/env python3
"""
CLI entrypoint for Pokemon Stock Bot operations
Usage: python -m pokemon_bot.cli --help
"""
import asyncio
import argparse
import logging
from typing import Optional

from utils.config import Config
from utils.logger import setup_logger
from monitors.generic_monitor import GenericStoreMonitor
from bot.daily_scheduler import DailyScanScheduler


async def run_daily_scan(monitor: GenericStoreMonitor, output_file: Optional[str] = None):
    """Run a daily scan and optionally save to file"""
    print("🌅 Starting daily scan...")
    
    # Load store configs
    store_configs = monitor.load_store_configs()
    
    # Focus on NZ stores
    nz_stores = {k: v for k, v in store_configs.items() if k.endswith('_nz')}
    
    scan_results = []
    
    for store_id, config in nz_stores.items():
        print(f"📍 Scanning {config['name']}...")
        
        try:
            if store_id == 'novagames_nz':
                # Use the working Nova Games scanner
                products = await monitor.scan_nova_games()
                scan_results.extend(products)
                print(f"  ✅ Found {len(products)} products in stock")
            else:
                print(f"  ⏭️  {config['name']} scanner not implemented yet")
        
        except Exception as e:
            print(f"  ❌ Error scanning {config['name']}: {e}")
    
    # Output results
    if output_file:
        with open(output_file, 'w') as f:
            f.write(f"Daily Scan Results - {len(scan_results)} products found\n")
            f.write("=" * 50 + "\n\n")
            
            for product in scan_results:
                f.write(f"• {product.get('name', 'Unknown Product')}\n")
                f.write(f"  Price: {product.get('price', 'Unknown')}\n")
                f.write(f"  URL: {product.get('url', 'Unknown')}\n\n")
        
        print(f"📄 Results saved to {output_file}")
    
    print(f"\n🎯 Scan complete! Found {len(scan_results)} products across {len(nz_stores)} stores.")


def main():
    """Main CLI entrypoint"""
    parser = argparse.ArgumentParser(
        description="Pokemon Stock Bot CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m pokemon_bot.cli --daily                 # Run daily scan
  python -m pokemon_bot.cli --daily --output scan.txt  # Save scan results
  python -m pokemon_bot.cli --check-config          # Validate configuration
  python -m pokemon_bot.cli --test-stores           # Test store connectivity
        """
    )
    
    parser.add_argument('--daily', action='store_true',
                       help='Run a daily scan of all stores')
    parser.add_argument('--output', type=str,
                       help='Save scan results to file')
    parser.add_argument('--check-config', action='store_true',
                       help='Validate configuration')
    parser.add_argument('--test-stores', action='store_true',
                       help='Test connectivity to all stores')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    logger = setup_logger()
    
    # Load config
    config = Config()
    
    if args.check_config:
        try:
            config.validate()
            print("✅ Configuration is valid")
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            return 1
    
    elif args.daily:
        try:
            monitor = GenericStoreMonitor(config)
            asyncio.run(run_daily_scan(monitor, args.output))
        except Exception as e:
            logger.error(f"Daily scan failed: {e}")
            return 1
    
    elif args.test_stores:
        print("🔍 Testing store connectivity...")
        # This would test basic connectivity to each store
        monitor = GenericStoreMonitor(config)
        store_configs = monitor.load_store_configs()
        
        for store_id, store_config in store_configs.items():
            if store_id.endswith('_nz'):
                print(f"  📡 {store_config['name']}: Connection test not implemented")
    
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())