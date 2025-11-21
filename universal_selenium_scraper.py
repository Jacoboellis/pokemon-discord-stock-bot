#!/usr/bin/env python3
"""
Universal Selenium Scraper for NZ Pokemon TCG Stores
Supports: Kmart NZ, The Warehouse NZ, JB Hi-Fi NZ, and EB Games NZ
"""

import time
import re
import asyncio
import aiohttp
import random
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.logger import setup_logger

logger = setup_logger(__name__)

class UniversalSeleniumScraper:
    """Universal scraper for NZ stores using Selenium with advanced bot protection bypass"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        
        # Store configurations
        self.store_configs = {
            'mightyape_nz': {
                'name': 'Mighty Ape NZ',
                'base_url': 'https://www.mightyape.co.nz',
                'search_url': 'https://www.mightyape.co.nz/mn/shop/?q=pokemon+tcg',
                'product_selectors': [
                    '.product-item', '.product-tile', '.search-result',
                    '[data-product-id]', '.product', '.item'
                ],
                'name_selectors': [
                    'h3 a', 'h2 a', '.product-name a', '.product-title a',
                    '.title a', 'a[title]'
                ],
                'price_selectors': [
                    '.price', '.current-price', '.product-price',
                    '.cost', '.dollar'
                ]
            },
            'kmart_nz': {
                'name': 'Kmart NZ',
                'base_url': 'https://www.kmart.co.nz',
                'search_url': 'https://www.kmart.co.nz/search/?text=pokemon',
                'product_selectors': [
                    '.product-item', '.product-tile', '[data-product-id]',
                    '.product', '.search-result-item'
                ],
                'name_selectors': [
                    'h3 a', 'h2 a', '.product-name a', '.product-title a',
                    '.name a', '[data-test-id="product-title"]'
                ],
                'price_selectors': [
                    '.price', '.current-price', '.product-price', 
                    '[data-test-id="price"]', '.cost'
                ]
            },
            'warehouse_nz': {
                'name': 'The Warehouse NZ',
                'base_url': 'https://www.thewarehouse.co.nz',
                'search_url': 'https://www.thewarehouse.co.nz/search?q=pokemon',
                'product_selectors': [
                    '.product-item', '.product-tile', '.search-result-item',
                    '[data-product-id]', '.product-card'
                ],
                'name_selectors': [
                    'h3 a', 'h2 a', '.product-name a', '.product-title a',
                    '.title a', '[data-test-id="product-name"]'
                ],
                'price_selectors': [
                    '.price', '.current-price', '.product-price',
                    '[data-test-id="price"]', '.dollar-value'
                ]
            },
            'jbhifi_nz': {
                'name': 'JB Hi-Fi NZ',
                'base_url': 'https://www.jbhifi.co.nz',
                'search_url': 'https://www.jbhifi.co.nz/search?query=pokemon%20tcg',
                'product_selectors': [
                    '[data-testid*="product"]',  # This is the correct selector!
                    'div[data-testid="product-tile"]',  # More specific version
                    '.product-tile'  # Fallback
                ],
                'name_selectors': [
                    '[data-testid="product-title"]',
                    'h3', 'h4', 'a[title]', '.product-title'
                ],
                'price_selectors': [
                    '[data-testid="price"]',
                    '.price', '.current-price', '.product-price'
                ],
                'wait_time': 8,  # Extra time for heavy JS
                'custom_extraction': True  # Use custom extraction method
            },
            'ebgames_nz': {
                'name': 'EB Games NZ',
                'base_url': 'https://www.ebgames.co.nz',
                'search_url': 'https://www.ebgames.co.nz/search?q=Pokemon%20tcg',
                'product_selectors': [
                    '.product-item', '.singleProduct', '.product',
                    '[class*="product"]', '.search-result-item'
                ],
                'name_selectors': [
                    'h3 a', 'h2 a', 'h4 a', '.product-name a',
                    '.product-title a', 'a.product-link'
                ],
                'price_selectors': [
                    '.price', '.product-price', '.buyNew', '.current-price',
                    '[class*="price"]', '.cost'
                ]
            },
            'pbtech_nz': {
                'name': 'PB Tech NZ',
                'base_url': 'https://www.pbtech.co.nz',
                'search_url': 'https://www.pbtech.co.nz/search?sf=pokemon+tcg&search_type=prediction',
                'product_selectors': [
                    'a.js-product-link.product-link.uniqueID',  # Exact selector for product containers
                    'a[data-product-code]',  # Fallback selector
                    '.product-link'  # Generic fallback
                ],
                'name_selectors': [
                    'img[alt]',  # Product name is in image alt text
                    'title',  # Also in title attribute
                    'text'  # Direct text extraction
                ],
                'price_selectors': [
                    '[data-price]',  # Price is in data-price attribute
                    '.price', '.cost'  # Standard fallbacks
                ],
                'wait_time': 4,  # Wait for JS to load
                'custom_extraction': True  # Need custom logic for this site
            },
            'novagames_nz': {
                'name': 'Nova Games NZ',
                'base_url': 'https://novagames.co.nz',
                'search_url': 'https://novagames.co.nz/collections/pokemon',
                'simple_http': True  # Use HTTP instead of Selenium
            },
            'cardmerchant_nz': {
                'name': 'Card Merchant NZ', 
                'base_url': 'https://cardmerchant.co.nz',
                'search_url': 'https://cardmerchant.co.nz/collections/pokemon-sealed',
                'simple_http': True  # Use HTTP instead of Selenium
            }
        }
    
    def setup_driver(self):
        """Setup Chrome driver with advanced stealth options and Cloudflare bypass"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Advanced stealth options to avoid bot detection and bypass Cloudflare
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # Faster loading
        chrome_options.add_argument('--disable-javascript')  # Bypass some bot detection
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Randomized user agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        import random
        selected_user_agent = random.choice(user_agents)
        chrome_options.add_argument(f'--user-agent={selected_user_agent}')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Execute stealth scripts to hide automation
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            self.driver.execute_script("window.chrome = {runtime: {}}")
            
            logger.info(f"Chrome driver setup successful with user agent: {selected_user_agent}")
            return True
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False

    def handle_cloudflare(self):
        """Check for and handle Cloudflare protection"""
        try:
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Check for Cloudflare indicators
            cloudflare_indicators = [
                'checking your browser before accessing',
                'cloudflare',
                'please wait while we check your browser',
                'ddos protection by cloudflare'
            ]
            
            if any(indicator in page_source for indicator in cloudflare_indicators):
                logger.info("Cloudflare detected, waiting for bypass...")
                
                # Wait for Cloudflare to complete (up to 30 seconds)
                wait_time = 0
                max_wait = 30
                
                while wait_time < max_wait:
                    time.sleep(2)
                    wait_time += 2
                    
                    # Check if we've moved past Cloudflare
                    new_url = self.driver.current_url
                    new_source = self.driver.page_source.lower()
                    
                    if (new_url != current_url or 
                        not any(indicator in new_source for indicator in cloudflare_indicators)):
                        logger.info(f"Cloudflare bypassed after {wait_time} seconds")
                        return True
                
                logger.warning(f"Cloudflare bypass may have failed after {max_wait} seconds")
                return False
            
            return True  # No Cloudflare detected
            
        except Exception as e:
            logger.error(f"Error handling Cloudflare: {e}")
            return False

    def scroll_to_load_all(self, max_scrolls=10):
        """Scroll down to load all products"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_pause_time = 1.5
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
    
    async def get_store_products(self, store_key: str) -> List[Dict[str, Any]]:
        """Get products from a store using either HTTP or Selenium based on store config"""
        if store_key not in self.store_configs:
            logger.error(f"Unknown store: {store_key}")
            return []
        
        store_config = self.store_configs[store_key]
        
        # Use simple HTTP for stores that don't need Selenium
        if store_config.get('simple_http'):
            return await self.get_store_products_http(store_key)
        
        # Use Selenium for complex stores
        return await self.get_store_products_selenium(store_key)
    
    async def get_store_products_http(self, store_key: str) -> List[Dict[str, Any]]:
        """Simple HTTP scraping for stores without bot protection"""
        store_config = self.store_configs[store_key]
        url = store_config['search_url']
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup_obj = soup(html, 'html.parser')
                        
                        products = []
                        product_links = soup_obj.find_all('a', href=re.compile(r'/products/'))
                        
                        for link in product_links:
                            try:
                                title = link.get_text().strip()
                                href = link.get('href', '')
                                
                                # Filter for actual products with meaningful titles
                                if title and len(title) > 5 and not any(skip in title.lower() 
                                    for skip in ['sold out', 'addtocart', 'add to cart']):
                                    
                                    # Extract price (simple approach)
                                    price = 0.0
                                    price_elem = link.find_parent().find(text=re.compile(r'\$\d+'))
                                    if price_elem:
                                        price_match = re.search(r'\$(\d+(?:\.\d{2})?)', price_elem)
                                        if price_match:
                                            price = float(price_match.group(1))
                                    
                                    products.append({
                                        'name': title,
                                        'price': price,
                                        'url': f"{store_config['base_url']}{href}",
                                        'store': store_config['name'],
                                        'stock_status': 'In Stock',
                                        'sku': self.extract_sku_from_url(href)
                                    })
                                    
                            except Exception as e:
                                logger.debug(f"Error parsing product from {store_config['name']}: {e}")
                                continue
                        
                        logger.info(f"Found {len(products)} products from {store_config['name']} via HTTP")
                        return products
                        
                    else:
                        logger.error(f"{store_config['name']} returned status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"HTTP scraping error for {store_config['name']}: {e}")
            return []
    
    async def get_store_products_selenium(self, store_key: str) -> List[Dict[str, Any]]:
        """Get Pokemon TCG products from specified store"""
        if store_key not in self.store_configs:
            logger.error(f"Unknown store: {store_key}")
            return []
        
        if not self.setup_driver():
            return []
        
        store_config = self.store_configs[store_key]
        products = []
        
        try:
            logger.info(f"Accessing {store_config['name']}: {store_config['search_url']}")
            
            self.driver.get(store_config['search_url'])
            
            # Handle Cloudflare if present
            if not self.handle_cloudflare():
                logger.warning(f"Failed to bypass Cloudflare for {store_config['name']}")
                # Continue anyway, sometimes it still works
            
            # Wait for page to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                logger.error(f"{store_config['name']} page load timeout")
                return []
            
            # Check if we got blocked
            page_title = self.driver.title.lower()
            page_source = self.driver.page_source.lower()
            
            if any(blocked in page_title for blocked in ["access denied", "403", "blocked", "error"]):
                logger.error(f"{store_config['name']} access denied - bot detection likely triggered")
                return []
                
            if any(blocked in page_source for blocked in ["access denied", "captcha", "robot"]):
                logger.warning(f"{store_config['name']} may have bot detection measures")
            
            # Special handling for sites with heavy JavaScript (like JB Hi-Fi)
            wait_time = store_config.get('wait_time', 3)
            logger.info(f"Waiting {wait_time} seconds for {store_config['name']} content to load...")
            time.sleep(wait_time)
            
            # Scroll to load all products
            self.scroll_to_load_all()
            
            # Get page source
            page_html = self.driver.page_source
            page_soup = soup(page_html, "html.parser")
            
            # Special handling for JB Hi-Fi NZ
            if store_key == 'jbhifi_nz':
                products = self.extract_jbhifi_products(page_soup)
            else:
                # Standard extraction for other stores
                # Try to find product containers
                containers = []
                for selector in store_config['product_selectors']:
                    containers = page_soup.select(selector)
                    if containers:
                        logger.info(f"Found {len(containers)} potential products using selector: {selector}")
                        break
                
                if not containers:
                    logger.warning(f"No product containers found for {store_config['name']}")
                    # Save HTML for debugging
                    with open(f"data/{store_key}_debug.html", "w", encoding="utf-8") as f:
                        f.write(page_html)
                    return []
                
                # Parse each product
                for container in containers:
                    try:
                        product = self.parse_product_container(container, store_config)
                        if product and self.is_pokemon_tcg_product(product['name']):
                            products.append(product)
                    except Exception as e:
                        logger.debug(f"Error parsing product container: {e}")
                        continue
            
            logger.info(f"Found {len(products)} Pokemon TCG products on {store_config['name']}")
            
        except Exception as e:
            logger.error(f"Error scraping {store_config['name']}: {e}")
        finally:
            if self.driver:
                self.driver.quit()
        
        return products
    
    def extract_jbhifi_products(self, soup) -> List[Dict[str, Any]]:
        """Custom extraction method for JB Hi-Fi NZ due to obfuscated classes"""
        products = []
        
        try:
            # Find divs containing Pokemon TCG content
            pokemon_containers = []
            for div in soup.find_all('div'):
                text = div.get_text().lower()
                if 'pokemon' in text and 'tcg' in text:
                    # Skip large containers (likely page containers)
                    if len(text) < 500:
                        pokemon_containers.append(div)
            
            logger.info(f"Found {len(pokemon_containers)} potential JB Hi-Fi containers")
            
            seen_products = set()
            
            for container in pokemon_containers[:20]:  # Limit to prevent spam
                try:
                    text = container.get_text(strip=True)
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    
                    # Extract product name
                    product_name = None
                    for line in lines:
                        if 'pokemon' in line.lower() and 10 < len(line) < 100:
                            # Clean up common artifacts
                            clean_line = line.replace('POKEMON TCG', '').replace('POKEMON TRADING CARD GAME', '').strip()
                            if clean_line and clean_line not in seen_products:
                                product_name = clean_line
                                break
                    
                    if not product_name:
                        continue
                        
                    # Extract price from container
                    price = 0.0
                    for line in lines:
                        if '$' in line and len(line) < 30:
                            # Extract price number
                            import re
                            price_match = re.search(r'\$(\d+(?:\.\d{2})?)', line)
                            if price_match:
                                price = float(price_match.group(1))
                                break
                    
                    # Extract URL
                    url = None
                    a_tag = container.find('a')
                    if a_tag and a_tag.get('href'):
                        href = a_tag.get('href')
                        if href.startswith('/'):
                            url = f"https://www.jbhifi.co.nz{href}"
                        else:
                            url = href
                    
                    # Generate SKU from product name
                    sku = self.generate_sku(product_name)
                    
                    if product_name and product_name not in seen_products:
                        product = {
                            'name': product_name,
                            'price': price,
                            'status': 'Available' if price > 0 else 'Price TBA',
                            'url': url or f"https://www.jbhifi.co.nz/search?query=pokemon%20tcg",
                            'sku': sku
                        }
                        products.append(product)
                        seen_products.add(product_name)
                        
                except Exception as e:
                    logger.debug(f"Error processing JB Hi-Fi container: {e}")
                    continue
                    
            logger.info(f"Extracted {len(products)} unique JB Hi-Fi products")
            
        except Exception as e:
            logger.error(f"Error in JB Hi-Fi extraction: {e}")
            
        return products
    
    def parse_product_container(self, container, store_config) -> Optional[Dict[str, Any]]:
        """Parse individual product container"""
        
        # Special handling for PB Tech
        if 'pbtech' in store_config.get('name', '').lower():
            return self.parse_pbtech_product(container)
        
        product = {}
        
        # Extract product name and URL
        for selector in store_config['name_selectors']:
            name_element = container.select_one(selector)
            if name_element:
                product['name'] = name_element.get_text(strip=True)
                # Get product URL if available
                href = name_element.get('href')
                if href:
                    if href.startswith('/'):
                        product['url'] = f"{store_config['base_url']}{href}"
                    else:
                        product['url'] = href
                break
        
        if not product.get('name'):
            # Try without link
            for selector in ['h3', 'h2', 'h4', '.product-name', '.product-title']:
                name_element = container.select_one(selector)
                if name_element:
                    product['name'] = name_element.get_text(strip=True)
                    break
        
        if not product.get('name'):
            return None
        
        # Extract price
        for selector in store_config['price_selectors']:
            price_element = container.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                price = self.extract_price(price_text)
                if price:
                    product['price'] = price
                    break
        
        # Determine stock status
        container_text = container.get_text().lower()
        product['status'] = self.determine_stock_status(container_text)
        
        # Add store info
        product['store'] = store_config['name']
        product['sku'] = self.extract_sku_from_url(product.get('url', ''))
        
        return product
    
    def parse_pbtech_product(self, container) -> Optional[Dict[str, Any]]:
        """Special parsing for PB Tech products"""
        # PB Tech structure: a.js-product-link with data-product-code
        product_code = container.get('data-product-code')
        if not product_code:
            return None
            
        product = {}
        
        # Extract product name from image alt text or title
        img_elem = container.select_one('img[alt]')
        if img_elem:
            product['name'] = img_elem.get('alt', '').strip()
        
        # If no name from image, try title attribute
        if not product.get('name'):
            title = container.get('title', '').strip()
            if title:
                product['name'] = title
        
        # Extract URL from href
        href = container.get('href', '')
        if href:
            if href.startswith('/'):
                product['url'] = f"https://www.pbtech.co.nz{href}"
            else:
                product['url'] = href
        
        # Extract price from data-price attribute or price elements
        price_text = container.get('data-price', '')
        if not price_text:
            # Look for price in child elements
            price_elem = container.select_one('.price, [data-price], .product-price')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
        
        if price_text:
            price = self.extract_price(price_text)
            if price:
                product['price'] = price
        
        # Set store info
        product['store'] = 'PB Tech NZ'
        product['sku'] = product_code
        product['status'] = 'available'  # PB Tech doesn't show out of stock items typically
        
        return product if product.get('name') else None

    def extract_sku_from_url(self, url: str) -> str:
        """Extract SKU from product URL"""
        import re
        
        # Look for product ID in URL
        sku_patterns = [
            r'/([0-9]+)',  # Basic numeric ID
            r'[?&]id=([^&]+)',  # Query parameter
            r'/products/([^/?]+)',  # Product slug
            r'[?&]sku=([^&]+)'  # SKU parameter
        ]
        
        for pattern in sku_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return ''
    
    def generate_sku(self, product_name: str) -> str:
        """Generate a normalized SKU-like slug from a product name.
        
        This provides a lightweight fallback SKU generation for sites where
        an explicit SKU isn't available. It lowercases, normalizes the
        'pokémon' character, removes non-alphanumeric characters (except
        spaces and hyphens), collapses whitespace to single hyphens and
        trims the result to a reasonable length.
        """
        import re
        
        if not product_name:
            return ''
        
        name = product_name.lower()
        # Normalize common unicode forms
        name = name.replace('pokémon', 'pokemon')
        # Remove characters that are not letters, numbers, spaces or hyphens
        name = re.sub(r'[^a-z0-9\s-]', '', name)
        # Collapse whitespace to single hyphen
        name = re.sub(r'\s+', '-', name.strip())
        # Truncate to 64 chars to keep SKU manageable
        return name[:64]
        import re
        
        # Remove common price prefixes/suffixes and extract number
        price_match = re.search(r'[\$]?([0-9]+\.?[0-9]*)', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group(1))
            except ValueError:
                pass
        return 0.0
    
    def determine_stock_status(self, container_text: str) -> str:
        """Determine stock status from container text"""
        stock_indicators = {
            'Out Of Stock': ['out of stock', 'sold out', 'unavailable', 'temporarily unavailable'],
            'Preorder': ['pre-order', 'preorder', 'coming soon', 'available soon'],
            'In Stock': ['add to cart', 'buy now', 'in stock', 'available', 'add to bag']
        }
        
        for status, indicators in stock_indicators.items():
            for indicator in indicators:
                if indicator in container_text:
                    return status
        
        # Default to in stock if we can't determine
        return 'In Stock'
    
    def extract_sku_from_url(self, url: str) -> str:
        """Extract SKU from product URL"""
        import re
        
        # Look for product ID in URL
        sku_patterns = [
            r'/([0-9]+)',  # Basic numeric ID
            r'[?&]id=([^&]+)',  # Query parameter
            r'/products/([^/?]+)',  # Product slug
            r'[?&]sku=([^&]+)'  # SKU parameter
        ]
        
        for pattern in sku_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return ''
    
    def is_pokemon_tcg_product(self, product_name: str) -> bool:
        """Check if product is Pokemon TCG related (not games or general merchandise)"""
        # TCG-specific keywords
        tcg_keywords = [
            'tcg', 'trading card', 'card game', 'booster', 'deck', 'tin', 'box', 'collection',
            'battle deck', 'theme deck', 'starter deck', 'elite trainer', 'premium collection',
            'bundle', 'pack', 'ex', 'gx', 'vmax', 'vstar', 'v-max', 'v-star',
            'ultra premium', 'trainer box', 'card set', 'expansion', 'pokémon cards',
            'pokemon cards'
        ]
        
        # Exclude non-TCG Pokemon items
        exclude_keywords = [
            'nintendo switch', 'switch', 'game boy', 'nintendo ds', '3ds', 'console', 'controller', 'case',
            'towel', 'tumbler', 'mug', 'plush', 'figure', 'shirt', 'clothing', 'apparel',
            'keychain', 'wallet', 'bag', 'backpack', 'legends z-a', 'legends: z-a',
            'sword', 'shield', 'brilliant diamond', 'shining pearl', 'arceus',
            'scarlet', 'violet', 'let\'s go', 'mystery dungeon', 'unite',
            'sleep', 'go', 'quest', 'rumble', 'stadium', 'snap', 'ranch',
            'video game', 'videogame', 'game', 'cd', 'dvd', 'blu-ray', 'software',
            'toy', 'puzzle', 'sticker', 'poster'
        ]
        
        name_lower = product_name.lower()
        
        # Must contain "pokemon" and at least one TCG keyword
        has_pokemon = any(keyword in name_lower for keyword in ['pokemon', 'pokémon'])
        has_tcg_keyword = any(keyword in name_lower for keyword in tcg_keywords)
        
        # Must not contain exclude keywords
        has_exclude_keyword = any(keyword in name_lower for keyword in exclude_keywords)
        
        return has_pokemon and has_tcg_keyword and not has_exclude_keyword

# Convenience functions for individual stores
async def get_mightyape_pokemon_tcg() -> List[Dict[str, Any]]:
    """Get Pokemon TCG products from Mighty Ape NZ"""
    scraper = UniversalSeleniumScraper(headless=True)
    return await scraper.get_store_products('mightyape_nz')

async def get_kmart_pokemon_tcg() -> List[Dict[str, Any]]:
    """Get Pokemon TCG products from Kmart NZ"""
    scraper = UniversalSeleniumScraper(headless=True)
    return await scraper.get_store_products('kmart_nz')

async def get_warehouse_pokemon_tcg() -> List[Dict[str, Any]]:
    """Get Pokemon TCG products from The Warehouse NZ"""
    scraper = UniversalSeleniumScraper(headless=True)
    return await scraper.get_store_products('warehouse_nz')

async def get_jbhifi_pokemon_tcg() -> List[Dict[str, Any]]:
    """Get Pokemon TCG products from JB Hi-Fi NZ"""
    scraper = UniversalSeleniumScraper(headless=True)
    return await scraper.get_store_products('jbhifi_nz')

async def get_ebgames_pokemon_tcg() -> List[Dict[str, Any]]:
    """Get Pokemon TCG products from EB Games NZ"""
    scraper = UniversalSeleniumScraper(headless=True)
    return await scraper.get_store_products('ebgames_nz')

async def get_pbtech_pokemon_tcg() -> List[Dict[str, Any]]:
    """Get Pokemon TCG products from PB Tech NZ"""
    scraper = UniversalSeleniumScraper(headless=True)
    return await scraper.get_store_products('pbtech_nz')

async def test_all_stores():
    """Test all NZ stores for Pokemon TCG products"""
    print("🧪 Testing Universal Selenium Scraper")
    print("=" * 60)
    
    stores = ['mightyape_nz', 'kmart_nz', 'warehouse_nz', 'jbhifi_nz', 'ebgames_nz', 'pbtech_nz']
    total_products = 0
    
    for store_key in stores:
        print(f"\n🏪 Testing {store_key.replace('_', ' ').title()}...")
        
        scraper = UniversalSeleniumScraper(headless=True)
        products = await scraper.get_store_products(store_key)
        
        store_name = scraper.store_configs[store_key]['name']
        
        if products:
            print(f"✅ Found {len(products)} Pokemon TCG products:")
            for i, product in enumerate(products[:3]):  # Show first 3
                print(f"   {i+1}. {product['name'][:60]}...")
                print(f"      ${product.get('price', 0):.2f} - {product.get('status', 'Unknown')}")
            
            if len(products) > 3:
                print(f"   ... and {len(products) - 3} more products")
            
            total_products += len(products)
        else:
            print(f"❌ No Pokemon TCG products found or store unavailable")
    
    print(f"\n🎯 Total Pokemon TCG products found across all stores: {total_products}")

if __name__ == "__main__":
    asyncio.run(test_all_stores())