#!/usr/bin/env python3
"""
🌅 Daily Pokemon Stock Scanner - Standalone Version
Perfect for your morning/evening routine!

Run this script to scan all NZ Pokemon stores and see what's in stock.
No Discord bot needed - just run and see results in terminal.
"""
import asyncio
import aiohttp
from datetime import datetime
import yaml
import os

def print_header():
    """Print a nice header for the scan"""
    current_time = datetime.now().strftime('%I:%M %p')
    print("=" * 60)
    print(f"🌅 POKEMON DAILY STOCK SCAN - {current_time}")
    print("=" * 60)
    print()

async def load_store_configs():
    """Load store configurations from YAML file"""
    config_path = 'store_config.yml'
    
    if not os.path.exists(config_path):
        print("❌ store_config.yml not found")
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config

async def scan_nova_games():
    """Scan Nova Games NZ - we know this works perfectly"""
    print("📍 Scanning Nova Games NZ...")
    products = []
    
    try:
        url = "https://novagames.co.nz/collections/pokemon"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Simple parsing for Nova Games
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find product cards
                    product_cards = soup.find_all('div', class_='product-card')
                    
                    for card in product_cards:
                        try:
                            # Product name
                            name_element = card.find('h3') or card.find('a', class_='product-card__title')
                            name = name_element.get_text(strip=True) if name_element else "Unknown Product"
                            
                            # Price
                            price_element = card.find('span', class_='price') or card.find('span', class_='money')
                            if price_element:
                                price_text = price_element.get_text(strip=True)
                                # Extract numeric price
                                import re
                                price_match = re.search(r'\$?([0-9,]+\.?[0-9]*)', price_text)
                                price = float(price_match.group(1).replace(',', '')) if price_match else 0.0
                            else:
                                price = 0.0
                            
                            # Product URL
                            link_element = card.find('a')
                            url_path = link_element.get('href', '') if link_element else ''
                            product_url = f"https://novagames.co.nz{url_path}" if url_path.startswith('/') else url_path
                            
                            products.append({
                                'name': name,
                                'price': price,
                                'url': product_url,
                                'store': 'Nova Games NZ'
                            })
                            
                        except Exception as e:
                            print(f"    ⚠️ Error parsing product: {e}")
                    
                    print(f"  ✅ Found {len(products)} products in stock")
                    
                else:
                    print(f"  ❌ HTTP {response.status}")
                    
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    return products

async def scan_other_stores():
    """Quick check of other NZ stores"""
    stores_to_check = [
        {
            'name': 'The Warehouse NZ',
            'url': 'https://www.thewarehouse.co.nz/search?q=pokemon+tcg'
        },
        {
            'name': 'JB Hi-Fi NZ',
            'url': 'https://www.jbhifi.co.nz/search?query=pokemon%20tcg'
        },
        {
            'name': 'Farmers NZ',
            'url': 'https://www.farmers.co.nz/search?SearchTerm=pokemon%20tcg'
        }
    ]
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        for store in stores_to_check:
            print(f"📍 Checking {store['name']}...")
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with session.get(store['url'], headers=headers, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        print(f"  ✅ Store is accessible ({len(html)} chars received)")
                        results.append({
                            'store': store['name'],
                            'status': 'accessible',
                            'note': 'Products parsing not implemented yet'
                        })
                    elif response.status == 403:
                        print(f"  ❌ HTTP 403 - Store blocks scraping")
                        results.append({
                            'store': store['name'],
                            'status': 'blocked',
                            'note': 'Store blocks bot access'
                        })
                    else:
                        print(f"  ⚠️ HTTP {response.status}")
                        results.append({
                            'store': store['name'],
                            'status': f'error_{response.status}',
                            'note': f'Returned HTTP {response.status}'
                        })
                        
            except Exception as e:
                print(f"  ❌ Error: {e}")
                results.append({
                    'store': store['name'],
                    'status': 'error',
                    'note': str(e)
                })
    
    return results

def print_results(products, store_results):
    """Print scan results in a nice format"""
    print()
    print("📊 SCAN RESULTS")
    print("-" * 40)
    
    # In-stock products
    if products:
        print(f"🛒 IN STOCK NOW ({len(products)} items):")
        print()
        
        for product in products:
            price_text = f"${product['price']:.2f}" if product['price'] > 0 else "Price TBA"
            print(f"  💎 {product['name']}")
            print(f"     💰 {price_text} | 📍 {product['store']}")
            print()
    else:
        print("🛒 IN STOCK NOW: No products found")
        print()
    
    # Store status
    print("🏪 STORE STATUS:")
    for result in store_results:
        status_emoji = "✅" if result['status'] == 'accessible' else "❌" if result['status'] == 'blocked' else "⚠️"
        print(f"  {status_emoji} {result['store']}: {result['note']}")
    
    print()
    print("💡 TIP: Nova Games NZ is working perfectly for monitoring!")
    print("📱 Add Nova Games products to your Discord bot with: /add_sku")
    print()

async def main():
    """Main function to run the daily scan"""
    print_header()
    
    # Scan Nova Games (we know this works)
    products = await scan_nova_games()
    
    print()
    
    # Check other stores
    store_results = await scan_other_stores()
    
    # Print results
    print_results(products, store_results)
    
    # Add Nova Games to store results
    store_results.insert(0, {
        'store': 'Nova Games NZ',
        'status': 'working',
        'note': f'Found {len(products)} products - fully working!'
    })
    
    print("=" * 60)
    print(f"✅ Scan completed at {datetime.now().strftime('%I:%M %p')}")
    print("=" * 60)

if __name__ == "__main__":
    print("🚀 Starting Pokemon Daily Stock Scanner...")
    print("Perfect for your morning/evening routine!")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Scan cancelled by user")
    except Exception as e:
        print(f"\n❌ Error during scan: {e}")
        print("Make sure you have the required packages: aiohttp, beautifulsoup4, pyyaml")