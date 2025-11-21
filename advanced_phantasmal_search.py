#!/usr/bin/env python3
"""
Advanced Phantasmal Flames searcher with bot protection bypass
Search across ALL NZ Pokemon TCG stores for the new set
"""

import asyncio
import logging
import time
import random
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedPhantasmalSearcher:
    def __init__(self):
        self.stores = {
            'jbhifi_nz': {
                'name': 'JB Hi-Fi NZ',
                'search_url': 'https://www.jbhifi.co.nz/search?query=phantasmal+flames+pokemon',
                'backup_url': 'https://www.jbhifi.co.nz/search?query=pokemon+phantasmal+flames',
                'product_selector': '.product-item',
                'name_selector': '.product-title a, h3 a',
                'price_selector': '.price, .product-price',
                'protection': 'light'
            },
            'ebgames_nz': {
                'name': 'EB Games NZ',
                'search_url': 'https://www.ebgames.co.nz/search?q=phantasmal+flames',
                'backup_url': 'https://www.ebgames.co.nz/search?q=pokemon+phantasmal',
                'product_selector': '.product-item, [class*="product"]',
                'name_selector': 'h3 a, h2 a, .product-name a',
                'price_selector': '.price, .product-price',
                'protection': 'cloudflare'
            },
            'pbtech_nz': {
                'name': 'PB Tech NZ',
                'search_url': 'https://www.pbtech.co.nz/search?sf=phantasmal+flames&search_type=prediction',
                'backup_url': 'https://www.pbtech.co.nz/search?sf=pokemon+phantasmal&search_type=prediction',
                'product_selector': 'a[data-product-code], .product-link',
                'name_selector': 'img[alt], [title]',
                'price_selector': '[data-price], .price',
                'protection': 'cloudflare'
            },
            'mightyape_nz': {
                'name': 'Mighty Ape NZ',
                'search_url': 'https://www.mightyape.co.nz/mn/shop/?q=phantasmal+flames+pokemon',
                'backup_url': 'https://www.mightyape.co.nz/mn/shop/?q=pokemon+phantasmal',
                'product_selector': '.product, [class*="product"]',
                'name_selector': '.product-name, h3 a',
                'price_selector': '.price, .product-price',
                'protection': 'captcha'
            }
        }
    
    def get_stealth_driver(self) -> webdriver.Chrome:
        """Create a stealthy Chrome driver to bypass bot detection"""
        options = Options()
        
        # Stealth options to avoid detection
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent rotation
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # Window size randomization
        options.add_argument(f'--window-size={random.randint(1200, 1920)},{random.randint(800, 1080)}')
        
        driver = webdriver.Chrome(options=options)
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver

    def wait_and_retry(self, min_wait=2, max_wait=5):
        """Random wait to appear more human-like"""
        wait_time = random.uniform(min_wait, max_wait)
        time.sleep(wait_time)

    async def search_store(self, store_key: str) -> List[Dict[str, Any]]:
        """Search a specific store for Phantasmal Flames"""
        store_config = self.stores[store_key]
        products = []
        
        print(f"\n🔍 Searching {store_config['name']} for Phantasmal Flames...")
        
        driver = self.get_stealth_driver()
        
        try:
            # Try main search URL first
            for attempt, url in enumerate([store_config['search_url'], store_config['backup_url']], 1):
                print(f"   Attempt {attempt}: {url}")
                
                driver.get(url)
                self.wait_and_retry(3, 8)  # Wait for page load
                
                # Handle different protection types
                if store_config['protection'] == 'cloudflare':
                    if await self.handle_cloudflare(driver):
                        print(f"   ✅ Bypassed Cloudflare protection!")
                    else:
                        print(f"   ❌ Cloudflare protection active, trying alternative...")
                        continue
                
                elif store_config['protection'] == 'captcha':
                    if await self.handle_captcha(driver):
                        print(f"   ✅ Bypassed captcha protection!")
                    else:
                        print(f"   ❌ Captcha protection active, trying alternative...")
                        continue
                
                # Look for products
                products = await self.extract_products(driver, store_config)
                if products:
                    print(f"   ✅ Found {len(products)} products!")
                    break
                else:
                    print(f"   ⚠️ No products found, trying backup URL...")
            
            return products
            
        except Exception as e:
            print(f"   ❌ Error searching {store_config['name']}: {e}")
            return []
        finally:
            driver.quit()

    async def handle_cloudflare(self, driver) -> bool:
        """Attempt to bypass Cloudflare protection"""
        try:
            # Check if we're on a Cloudflare challenge page
            if "Just a moment" in driver.page_source or "cloudflare" in driver.page_source.lower():
                print(f"   🔄 Cloudflare challenge detected, waiting...")
                
                # Wait up to 30 seconds for challenge to complete
                for i in range(30):
                    time.sleep(1)
                    if "Just a moment" not in driver.page_source:
                        return True
                    if i % 5 == 0:
                        print(f"   ⏳ Still waiting... ({i+1}s)")
                
                return False
            return True
        except Exception:
            return False

    async def handle_captcha(self, driver) -> bool:
        """Attempt to handle captcha systems"""
        try:
            if "captcha-delivery" in driver.page_source:
                print(f"   🔄 Captcha system detected...")
                # For now, just wait and see if it auto-resolves
                time.sleep(10)
                return "captcha-delivery" not in driver.page_source
            return True
        except Exception:
            return False

    async def extract_products(self, driver, store_config) -> List[Dict[str, Any]]:
        """Extract product information from the page"""
        products = []
        
        try:
            # Scroll to load dynamic content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            self.wait_and_retry(2, 4)
            
            # Find product containers
            containers = driver.find_elements(By.CSS_SELECTOR, store_config['product_selector'])
            print(f"   📦 Found {len(containers)} potential product containers")
            
            for container in containers[:20]:  # Limit to first 20 for performance
                try:
                    # Extract product name
                    name_elem = container.find_element(By.CSS_SELECTOR, store_config['name_selector'])
                    name = name_elem.text.strip() or name_elem.get_attribute('alt') or name_elem.get_attribute('title')
                    
                    if not name:
                        continue
                    
                    # Check if it's Phantasmal Flames related
                    name_lower = name.lower()
                    if not any(term in name_lower for term in ['phantasmal', 'phantom', 'flames']):
                        continue
                    
                    # Extract price
                    price = 'Not available'
                    try:
                        price_elem = container.find_element(By.CSS_SELECTOR, store_config['price_selector'])
                        price_text = price_elem.text.strip()
                        if price_text and '$' in price_text:
                            price = price_text
                    except NoSuchElementException:
                        pass
                    
                    # Extract URL
                    url = 'Not available'
                    try:
                        link_elem = container.find_element(By.CSS_SELECTOR, 'a')
                        href = link_elem.get_attribute('href')
                        if href:
                            url = href if href.startswith('http') else f"https://{store_config['name'].lower().split()[0]}.co.nz{href}"
                    except NoSuchElementException:
                        pass
                    
                    product = {
                        'name': name,
                        'price': price,
                        'url': url,
                        'store': store_config['name']
                    }
                    
                    products.append(product)
                    print(f"      ✅ {name} - {price}")
                    
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"   ❌ Error extracting products: {e}")
        
        return products

async def search_all_stores_for_phantasmal():
    """Main function to search all stores for Phantasmal Flames"""
    
    print("🔥 PHANTASMAL FLAMES SEARCH ACROSS ALL NZ STORES")
    print("=" * 60)
    print("Searching for the new Pokemon TCG set across all available retailers...")
    print()
    
    searcher = AdvancedPhantasmalSearcher()
    all_products = []
    
    # Search each store
    for store_key in searcher.stores.keys():
        products = await searcher.search_store(store_key)
        all_products.extend(products)
        
        # Wait between stores to avoid triggering more protections
        await asyncio.sleep(random.uniform(2, 5))
    
    # Generate comprehensive report
    print("\n" + "=" * 60)
    print("🎯 PHANTASMAL FLAMES COMPREHENSIVE REPORT")
    print("=" * 60)
    
    if all_products:
        print(f"📊 Total products found: {len(all_products)}")
        print(f"🏪 Stores with stock: {len(set(p['store'] for p in all_products))}")
        
        print("\n📦 ALL PHANTASMAL FLAMES PRODUCTS:")
        for i, product in enumerate(all_products, 1):
            print(f"{i:2d}. {product['name']}")
            print(f"     🏪 Store: {product['store']}")
            print(f"     💰 Price: {product['price']}")
            print(f"     🔗 URL: {product['url']}")
            print()
        
        # Price analysis
        prices = [p['price'] for p in all_products if '$' in p['price']]
        if prices:
            print("💰 PRICE ANALYSIS:")
            print(f"   Cheapest: {min(prices, key=lambda x: float(x.replace('$', '').replace(',', '')))} ")
            print(f"   Most expensive: {max(prices, key=lambda x: float(x.replace('$', '').replace(',', '')))}")
    else:
        print("❌ No Phantasmal Flames products found in any NZ store")
        print("\n🔍 This could mean:")
        print("   • Set hasn't been released in NZ yet")
        print("   • All stock is sold out")
        print("   • Different product naming is used")
        print("   • Bot protections blocked access to product data")

if __name__ == '__main__':
    asyncio.run(search_all_stores_for_phantasmal())