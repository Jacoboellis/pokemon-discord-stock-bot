#!/usr/bin/env python3
"""
EB Games NZ Pokemon TCG Scraper using Selenium
Adapted from EB Games CA scraper to work with NZ site and Pokemon products
"""

import time
import asyncio
from typing import List, Dict, Any
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.logger import setup_logger

logger = setup_logger(__name__)

class EBGamesNZSeleniumScraper:
    """EB Games NZ scraper using Selenium to bypass bot detection"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with stealth options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Anti-detection options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent to look more human
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return True
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def scroll_to_load_all(self, max_scrolls=10):
        """Scroll down to load all products"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_pause_time = 1.0
        scrolls = 0
        
        while scrolls < max_scrolls:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for page to load
            time.sleep(scroll_pause_time)
            
            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                # Try one more time
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    break
            
            last_height = new_height
            scrolls += 1
        
        logger.info(f"Completed scrolling after {scrolls} attempts")
    
    async def get_pokemon_products(self) -> List[Dict[str, Any]]:
        """Get Pokemon TCG products from EB Games NZ"""
        if not self.setup_driver():
            return []
        
        products = []
        
        try:
            # EB Games NZ Pokemon search URL
            pokemon_url = "https://www.ebgames.co.nz/search?q=pokemon"
            logger.info(f"Accessing EB Games NZ Pokemon search: {pokemon_url}")
            
            self.driver.get(pokemon_url)
            
            # Wait for page to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                logger.error("Page load timeout")
                return []
            
            # Check if we got blocked
            page_title = self.driver.title.lower()
            if "access denied" in page_title or "403" in page_title or "blocked" in page_title:
                logger.error("Access denied - bot detection likely triggered")
                return []
            
            # Wait a bit more for content to load
            time.sleep(3)
            
            # Scroll to load all products
            self.scroll_to_load_all()
            
            # Get page source
            page_html = self.driver.page_source
            page_soup = soup(page_html, "html.parser")
            
            # Try multiple possible product container selectors
            product_selectors = [
                "div.product-item",
                "div.singleProduct", 
                "div.product",
                "div[class*='product']",
                "article.product",
                ".search-result-item"
            ]
            
            containers = []
            for selector in product_selectors:
                containers = page_soup.select(selector)
                if containers:
                    logger.info(f"Found {len(containers)} products using selector: {selector}")
                    break
            
            if not containers:
                logger.warning("No product containers found")
                # Save HTML for debugging
                with open("data/ebgames_debug.html", "w", encoding="utf-8") as f:
                    f.write(page_html)
                return []
            
            # Parse each product
            for container in containers:
                try:
                    product = self.parse_product_container(container)
                    if product and self.is_pokemon_product(product['name']):
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Error parsing product container: {e}")
                    continue
            
            logger.info(f"Found {len(products)} Pokemon products on EB Games NZ")
            
        except Exception as e:
            logger.error(f"Error scraping EB Games NZ: {e}")
        finally:
            if self.driver:
                self.driver.quit()
        
        return products
    
    def parse_product_container(self, container) -> Dict[str, Any]:
        """Parse individual product container"""
        product = {}
        
        # Try to extract product name
        name_selectors = [
            "h3 a", "h2 a", "h4 a", ".product-name a", 
            ".product-title a", "a.product-link"
        ]
        
        for selector in name_selectors:
            name_element = container.select_one(selector)
            if name_element:
                product['name'] = name_element.get_text(strip=True)
                # Get product URL if available
                href = name_element.get('href')
                if href:
                    if href.startswith('/'):
                        product['url'] = f"https://www.ebgames.co.nz{href}"
                    else:
                        product['url'] = href
                break
        
        if not product.get('name'):
            # Try without link
            name_selectors = ["h3", "h2", "h4", ".product-name", ".product-title"]
            for selector in name_selectors:
                name_element = container.select_one(selector)
                if name_element:
                    product['name'] = name_element.get_text(strip=True)
                    break
        
        if not product.get('name'):
            return None
        
        # Try to extract price
        price_selectors = [
            ".price", ".product-price", ".buyNew", ".current-price", 
            "[class*='price']", ".cost"
        ]
        
        for selector in price_selectors:
            price_element = container.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                price = self.extract_price(price_text)
                if price:
                    product['price'] = price
                    break
        
        # Try to determine stock status
        stock_indicators = {
            'in_stock': ['add to cart', 'buy now', 'in stock', 'available'],
            'out_of_stock': ['out of stock', 'sold out', 'unavailable'],
            'preorder': ['pre-order', 'preorder', 'coming soon']
        }
        
        container_text = container.get_text().lower()
        product['status'] = 'Unknown'
        
        for status, indicators in stock_indicators.items():
            for indicator in indicators:
                if indicator in container_text:
                    product['status'] = status.replace('_', ' ').title()
                    break
            if product.get('status') != 'Unknown':
                break
        
        # Default to in stock if we can't determine
        if product.get('status') == 'Unknown':
            product['status'] = 'In Stock'
        
        # Add store info
        product['store'] = 'EB Games NZ'
        product['sku'] = self.extract_sku_from_url(product.get('url', ''))
        
        return product
    
    def extract_price(self, price_text: str) -> float:
        """Extract numeric price from text"""
        import re
        
        # Remove common price prefixes/suffixes and extract number
        price_match = re.search(r'[\$]?([0-9]+\.?[0-9]*)', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group(1))
            except ValueError:
                pass
        return 0.0
    
    def extract_sku_from_url(self, url: str) -> str:
        """Extract SKU from product URL"""
        import re
        
        # Look for product ID in URL
        sku_match = re.search(r'/([0-9]+)', url)
        if sku_match:
            return sku_match.group(1)
        
        # Extract from product path
        if '/product/' in url:
            parts = url.split('/product/')[-1].split('-')
            if parts and parts[0].isdigit():
                return parts[0]
        
        return ''
    
    def is_pokemon_product(self, product_name: str) -> bool:
        """Check if product is Pokemon TCG related (not games or merchandise)"""
        # TCG-specific keywords
        tcg_keywords = [
            'tcg', 'trading card', 'card game', 'booster', 'deck', 'tin', 'box', 'collection',
            'battle deck', 'theme deck', 'starter deck', 'elite trainer', 'premium collection',
            'bundle', 'pack', 'ex', 'gx', 'vmax', 'vstar', 'v-max', 'v-star',
            'ultra premium', 'trainer box', 'card set', 'expansion'
        ]
        
        # Exclude non-TCG Pokemon items (games, merchandise, etc.)
        exclude_keywords = [
            'nintendo switch', 'switch', 'game boy', 'ds', 'console', 'controller', 'case',
            'towel', 'tumbler', 'mug', 'plush', 'figure', 'shirt', 'clothing',
            'keychain', 'wallet', 'bag', 'backpack', 'legends z-a', 'legends: z-a',
            'sword', 'shield', 'brilliant diamond', 'shining pearl', 'arceus',
            'scarlet', 'violet', 'let\'s go', 'mystery dungeon', 'unite',
            'sleep', 'go', 'quest', 'rumble', 'stadium', 'snap', 'ranch',
            'video game', 'videogame', 'game', 'cd', 'dvd', 'blu-ray'
        ]
        
        name_lower = product_name.lower()
        
        # Must contain "pokemon" and at least one TCG keyword
        has_pokemon = any(keyword in name_lower for keyword in ['pokemon', 'pokémon'])
        has_tcg_keyword = any(keyword in name_lower for keyword in tcg_keywords)
        
        # Must not contain exclude keywords
        has_exclude_keyword = any(keyword in name_lower for keyword in exclude_keywords)
        
        return has_pokemon and has_tcg_keyword and not has_exclude_keyword

async def test_ebgames_selenium():
    """Test the EB Games Selenium scraper"""
    print("🧪 Testing EB Games NZ Selenium Scraper")
    print("=" * 50)
    
    scraper = EBGamesNZSeleniumScraper(headless=True)  # Set to False to see browser
    products = await scraper.get_pokemon_products()
    
    if products:
        print(f"✅ Found {len(products)} Pokemon products:")
        for i, product in enumerate(products[:10]):  # Show first 10
            print(f"\n{i+1}. {product['name']}")
            print(f"   Price: ${product.get('price', 0):.2f}")
            print(f"   Status: {product.get('status', 'Unknown')}")
            print(f"   URL: {product.get('url', 'N/A')}")
    else:
        print("❌ No products found or scraping failed")

if __name__ == "__main__":
    asyncio.run(test_ebgames_selenium())