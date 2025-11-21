#!/usr/bin/env python3
"""
Comprehensive Pokemon TCG Market Survey for NZ
Check what's actually available right now across all accessible stores
"""

import asyncio
import time
import random
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

class NZPokemonMarketSurvey:
    def __init__(self):
        self.stores = {
            'jbhifi_nz': {
                'name': 'JB Hi-Fi NZ',
                'url': 'https://www.jbhifi.co.nz/search?query=pokemon+tcg',
                'container_selectors': ['.product-item', '.product', '[class*="product"]'],
                'name_selectors': ['.product-title a', 'h3 a', 'h2 a', '.product-name a'],
                'price_selectors': ['.price', '.product-price', '[class*="price"]'],
                'protection': False
            },
            'ebgames_nz': {
                'name': 'EB Games NZ',
                'url': 'https://www.ebgames.co.nz/search?q=pokemon+tcg',
                'container_selectors': ['[class*="product"]', '.product-item', '.search-result'],
                'name_selectors': ['h3 a', 'h2 a', '.product-name a', '.product-title a'],
                'price_selectors': ['.price', '.product-price', '.buyNew', '[class*="price"]'],
                'protection': True
            }
        }
    
    def get_stealth_driver(self):
        """Create anti-detection Chrome driver"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Randomize user agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        options.add_argument(f'--window-size={random.randint(1200, 1600)},{random.randint(800, 1200)}')
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    def extract_price(self, price_text: str) -> str:
        """Extract clean price from text"""
        if not price_text:
            return "Price not available"
        
        # Look for dollar amounts
        price_match = re.search(r'\$([0-9,]+\.?[0-9]*)', price_text)
        if price_match:
            return f"${price_match.group(1)}"
        return price_text.strip()
    
    def wait_for_cloudflare(self, driver, max_wait=30) -> bool:
        """Wait for Cloudflare to complete"""
        print("      🔄 Cloudflare detected, waiting...")
        for i in range(max_wait):
            if "Just a moment" not in driver.page_source and "cloudflare" not in driver.page_source.lower():
                print("      ✅ Cloudflare bypassed!")
                return True
            time.sleep(1)
            if i > 0 and i % 10 == 0:
                print(f"      ⏳ Still waiting... ({i}s)")
        print("      ❌ Cloudflare timeout")
        return False
    
    async def survey_store(self, store_key: str) -> List[Dict[str, Any]]:
        """Survey a single store for Pokemon TCG products"""
        store = self.stores[store_key]
        print(f"\n🏪 Surveying {store['name']}...")
        print(f"   🌐 URL: {store['url']}")
        
        driver = self.get_stealth_driver()
        products = []
        
        try:
            # Load the page
            driver.get(store['url'])
            await asyncio.sleep(random.uniform(3, 7))
            
            # Handle protection if needed
            if store['protection']:
                if "Just a moment" in driver.page_source or "cloudflare" in driver.page_source.lower():
                    if not self.wait_for_cloudflare(driver):
                        return products
            
            # Scroll to load dynamic content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            await asyncio.sleep(2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            await asyncio.sleep(3)
            
            # Try different container selectors
            containers = []
            for selector in store['container_selectors']:
                found_containers = driver.find_elements(By.CSS_SELECTOR, selector)
                if found_containers:
                    containers = found_containers
                    print(f"   📦 Found {len(containers)} containers with selector: {selector}")
                    break
            
            if not containers:
                print(f"   ❌ No product containers found")
                return products
            
            # Extract products from containers
            print(f"   🔍 Extracting products...")
            for i, container in enumerate(containers[:25]):  # Limit for performance
                try:
                    # Try to find product name
                    name = None
                    for name_selector in store['name_selectors']:
                        try:
                            name_elem = container.find_element(By.CSS_SELECTOR, name_selector)
                            name = name_elem.text.strip()
                            if name:
                                break
                        except NoSuchElementException:
                            continue
                    
                    if not name:
                        continue
                    
                    # Filter for Pokemon products only
                    if 'pokemon' not in name.lower():
                        continue
                    
                    # Extract price
                    price = "Price not available"
                    for price_selector in store['price_selectors']:
                        try:
                            price_elem = container.find_element(By.CSS_SELECTOR, price_selector)
                            price_text = price_elem.text.strip()
                            if price_text:
                                price = self.extract_price(price_text)
                                break
                        except NoSuchElementException:
                            continue
                    
                    # Extract URL
                    url = "URL not available"
                    try:
                        link_elem = container.find_element(By.CSS_SELECTOR, 'a')
                        href = link_elem.get_attribute('href')
                        if href:
                            url = href if href.startswith('http') else f"https://{store['name'].lower().split()[0]}.co.nz{href}"
                    except NoSuchElementException:
                        pass
                    
                    product = {
                        'name': name,
                        'price': price,
                        'url': url,
                        'store': store['name']
                    }
                    
                    products.append(product)
                    
                except Exception:
                    continue
            
            print(f"   ✅ Successfully extracted {len(products)} Pokemon TCG products")
            
        except Exception as e:
            print(f"   ❌ Error surveying {store['name']}: {e}")
        
        finally:
            driver.quit()
        
        return products

async def run_market_survey():
    """Run comprehensive Pokemon TCG market survey"""
    
    print("🎮 NEW ZEALAND POKEMON TCG MARKET SURVEY")
    print("=" * 60)
    print("Comprehensive check of current Pokemon TCG availability")
    print("Using advanced bot protection bypass techniques")
    print()
    
    survey = NZPokemonMarketSurvey()
    all_products = []
    
    # Survey each store
    for store_key in survey.stores.keys():
        products = await survey.survey_store(store_key)
        all_products.extend(products)
        
        # Show quick summary
        if products:
            print(f"   📊 Quick preview (first 3 products):")
            for i, product in enumerate(products[:3], 1):
                print(f"      {i}. {product['name']}")
                print(f"         💰 {product['price']}")
        
        # Wait between stores
        if len(survey.stores) > 1:
            wait_time = random.uniform(3, 8)
            print(f"   ⏳ Waiting {wait_time:.1f}s before next store...")
            await asyncio.sleep(wait_time)
    
    # Generate comprehensive report
    print("\n" + "=" * 60)
    print("📊 NEW ZEALAND POKEMON TCG MARKET REPORT")
    print("=" * 60)
    
    if all_products:
        print(f"🎯 Total Pokemon TCG products found: {len(all_products)}")
        print(f"🏪 Stores surveyed: {len(survey.stores)}")
        print(f"✅ Stores with products: {len(set(p['store'] for p in all_products))}")
        
        # Group by store
        by_store = {}
        for product in all_products:
            store = product['store']
            if store not in by_store:
                by_store[store] = []
            by_store[store].append(product)
        
        print(f"\n🏪 STORE BREAKDOWN:")
        for store, products in by_store.items():
            print(f"   • {store}: {len(products)} products")
        
        # Product analysis
        print(f"\n📦 ALL POKEMON TCG PRODUCTS AVAILABLE:")
        for i, product in enumerate(all_products, 1):
            print(f"{i:3d}. {product['name']}")
            print(f"      🏪 {product['store']}")
            print(f"      💰 {product['price']}")
            if product['url'] != "URL not available":
                print(f"      🔗 {product['url'][:80]}{'...' if len(product['url']) > 80 else ''}")
            print()
        
        # Set analysis
        print(f"🎲 SET ANALYSIS:")
        set_keywords = ['booster', 'deck', 'box', 'collection', 'tin', 'bundle', 'pack', 'elite', 'trainer']
        product_types = {}
        for keyword in set_keywords:
            matching = [p for p in all_products if keyword in p['name'].lower()]
            if matching:
                product_types[keyword] = len(matching)
        
        for product_type, count in sorted(product_types.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {product_type.title()}: {count} products")
        
        # Price analysis
        prices_with_values = []
        for product in all_products:
            price_text = product['price']
            if '$' in price_text:
                try:
                    price_match = re.search(r'\$([0-9,]+\.?[0-9]*)', price_text)
                    if price_match:
                        price_value = float(price_match.group(1).replace(',', ''))
                        prices_with_values.append(price_value)
                except ValueError:
                    pass
        
        if prices_with_values:
            print(f"\n💰 PRICE ANALYSIS:")
            print(f"   • Cheapest: ${min(prices_with_values):.2f}")
            print(f"   • Most expensive: ${max(prices_with_values):.2f}")
            print(f"   • Average price: ${sum(prices_with_values)/len(prices_with_values):.2f}")
            print(f"   • Products with prices: {len(prices_with_values)}/{len(all_products)}")
        
    else:
        print("❌ No Pokemon TCG products found in any store")
        print("\n🔍 This could indicate:")
        print("   • Bot protection blocking access")
        print("   • Different search terms needed")
        print("   • Products temporarily out of stock")
        print("   • Website structure changes")
    
    print(f"\n✅ Survey complete!")

if __name__ == '__main__':
    asyncio.run(run_market_survey())