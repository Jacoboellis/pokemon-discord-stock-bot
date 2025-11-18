#!/usr/bin/env python3
"""
Generic web scraper for any Pokemon store
Can handle multiple stores without individual monitor classes
"""

import re
import asyncio
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
from monitors.base_monitor import BaseMonitor
from utils.logger import setup_logger

logger = setup_logger(__name__)


class GenericStoreMonitor(BaseMonitor):
    """Generic monitor that can scrape any store based on configuration"""
    
    def __init__(self, config):
        super().__init__(config)
        self.store_configs = self.load_store_configs()
    
    def load_store_configs(self) -> Dict[str, Dict]:
        """Load store configurations - focused on New Zealand stores"""
        return {
            # === NEW ZEALAND STORES (Primary Focus) ===
            'novagames_nz': {
                'name': 'Nova Games NZ',
                'base_url': 'https://novagames.co.nz',
                'search_url': 'https://novagames.co.nz/collections/pokemon',
                'sku_url_pattern': r'/products/{sku}',  # /products/mega-evolution-booster-pack
                'price_selectors': ['.price', '.regular-price', '[class*="price"]'],
                'name_selector': 'h1',
                'stock_indicators': {
                    'in_stock': ['add to wishlist', 'available in-store'],  # If page exists, it's in stock
                    'out_of_stock': ['sold out', 'unavailable'],
                    'preorder': ['preorder', 'pre-order']
                }
            },
            'ebgames_nz': {
                'name': 'EB Games NZ',
                'base_url': 'https://www.ebgames.co.nz',
                'search_url': 'https://www.ebgames.co.nz/search?category=toys-hobbies&subcategory=toys-hobbies-trading-cards&attributes=franchise%3Apokemon',
                'sku_url_pattern': r'/product/[^/]+/(\d+)-',  # /product/toys-and-collectibles/331128-pokemon-tcg...
                'price_selectors': ['span[itemprop="price"]', 'span.price', '.price-current'],
                'name_selector': 'h1.product-title, h1',
                'sku_selector': 'span.r',  # <span class="r">331128</span>
                'stock_indicators': {
                    'in_stock': ['add to cart', 'add to wishlist'],
                    'out_of_stock': ['out of stock', 'sold out'],
                    'preorder': ['preorder', 'pre-order']
                }
            },
            'cardmerchant_nz': {
                'name': 'Card Merchant NZ',
                'base_url': 'https://cardmerchant.co.nz',
                'search_url': 'https://cardmerchant.co.nz/collections/pokemon-sealed/products.json',  # JSON API endpoint
                'sku_url_pattern': r'/products/([^/?]+)',  # /products/pkm-unova-poster-collection
                'price_selectors': ['.price', '.money', '[class*="price"]'],
                'name_selector': 'h1.product-title, h1, .product-name',
                'stock_indicators': {
                    'in_stock': ['add to cart', 'add to bag'],  # If shown, it's in stock
                    'out_of_stock': ['sold out', 'unavailable'],
                    'preorder': ['preorder', 'pre-order']
                }
            },
            'thewarehouse_nz': {
                'name': 'The Warehouse NZ',
                'base_url': 'https://www.thewarehouse.co.nz',
                'search_url': 'https://www.thewarehouse.co.nz/search?q={query}&lang=default&search-button=',
                'sku_url_pattern': r'/p/[^/]+/{sku}\.html',  # /p/pokemon-product/R2984751.html
                'price_selectors': ['.price', '.current-price', '[data-price]'],
                'name_selector': 'h1',
                'stock_indicators': {
                    'in_stock': ['add to cart'],
                    'out_of_stock': ['out of stock', 'sold out'],
                    'preorder': ['preorder', 'pre-order']
                }
            },
            'jbhifi_nz': {
                'name': 'JB Hi-Fi NZ',
                'base_url': 'https://www.jbhifi.co.nz',
                'search_url': 'https://www.jbhifi.co.nz/search?query={query}',
                'sku_url_pattern': '/[^/]+/{sku}/',
                'price_selectors': ['.price', '.product-price', '[class*="price"]'],
                'name_selector': 'h1',
                'stock_indicators': {
                    'in_stock': ['add to cart', 'buy now'],
                    'out_of_stock': ['out of stock', 'sold out'],
                    'preorder': ['preorder', 'pre-order']
                }
            },
            'kmart_nz': {
                'name': 'Kmart NZ',
                'base_url': 'https://www.kmart.co.nz',
                'search_url': 'https://www.kmart.co.nz/search/?searchTerm={query}',
                'sku_url_pattern': '/[^/]+/{sku}',
                'price_selectors': ['.price', '.product-price'],
                'name_selector': 'h1',
                'stock_indicators': {
                    'in_stock': ['add to cart'],
                    'out_of_stock': ['out of stock', 'sold out'],
                    'preorder': ['preorder']
                }
            },
            'farmers_nz': {
                'name': 'Farmers NZ',
                'base_url': 'https://www.farmers.co.nz',
                'search_url': 'https://www.farmers.co.nz/search?SearchTerm={query}',
                'sku_url_pattern': '/[^/]+/{sku}',
                'price_selectors': ['.price', '.current-price'],
                'name_selector': 'h1',
                'stock_indicators': {
                    'in_stock': ['add to cart', 'add to bag'],
                    'out_of_stock': ['out of stock', 'sold out'],
                    'preorder': ['preorder']
                }
            },
            
            # === INTERNATIONAL STORES (Available but not in Discord choices) ===
            # Note: These are removed from Discord slash command choices
            # but kept in code in case needed for manual testing
            'pokemon_center': {
                'name': 'Pokemon Center (US)',
                'base_url': 'https://www.pokemoncenter.com',
                'search_url': 'https://www.pokemoncenter.com/search?q={query}',
                'sku_url_pattern': '/product/{sku}',
                'price_selectors': ['.price', '.current-price'],
                'name_selector': 'h1',
                'stock_indicators': {
                    'in_stock': ['add to bag', 'add to cart'],
                    'out_of_stock': ['out of stock', 'sold out'],
                    'preorder': ['preorder', 'pre-order']
                }
            },
            'bestbuy': {
                'name': 'Best Buy (US)',
                'base_url': 'https://www.bestbuy.com',
                'search_url': 'https://www.bestbuy.com/site/searchpage.jsp?st={query}',
                'sku_url_pattern': '/site/[^/]+/{sku}',
                'price_selectors': ['.pricing-price__range', '.sr-only:contains("current price")'],
                'name_selector': 'h1',
                'stock_indicators': {
                    'in_stock': ['add to cart'],
                    'out_of_stock': ['sold out', 'out of stock'],
                    'preorder': ['preorder', 'pre-order']
                }
            },
            'target': {
                'name': 'Target (US)',
                'base_url': 'https://www.target.com',
                'search_url': 'https://www.target.com/s?searchTerm={query}',
                'sku_url_pattern': '/p/[^/]+/A-{sku}',
                'price_selectors': ['[data-test="product-price"]'],
                'name_selector': 'h1',
                'stock_indicators': {
                    'in_stock': ['add to cart'],
                    'out_of_stock': ['out of stock'],
                    'preorder': ['preorder']
                }
            }
        }

    async def check_stock(self, sku: str, product_url: str = None) -> Dict[str, Any]:
        """Check stock for a SKU across all configured stores or specific store"""
        # If product_url is provided, try to determine store from URL
        if product_url:
            store_name = self.detect_store_from_url(product_url)
            if store_name:
                return await self.check_store_specific(store_name, sku, product_url)
        
        # Otherwise, try all stores
        for store_name in self.store_configs:
            result = await self.check_store_specific(store_name, sku)
            if result['stock_status'] != 'Unknown':
                return result
        
        # Return unknown if no stores had the product
        return {
            'sku': sku,
            'stock_status': 'Unknown',
            'price': None,
            'product_name': None,
            'product_url': product_url
        }

    async def check_store_specific(self, store_name: str, sku: str, product_url: str = None) -> Dict[str, Any]:
        """Check stock for a specific store"""
        if store_name not in self.store_configs:
            return {
                'sku': sku,
                'stock_status': 'Unknown',
                'price': None,
                'product_name': None,
                'product_url': product_url
            }
        
        store_config = self.store_configs[store_name]
        
        try:
            # Find product URL if not provided
            if not product_url:
                product_url = await self.find_product_url(store_config, sku)
                if not product_url:
                    return {
                        'sku': sku,
                        'stock_status': 'Unknown',
                        'price': None,
                        'product_name': None,
                        'product_url': None
                    }
            
            # Get product page
            html_content = await self.safe_request(product_url)
            if not html_content:
                return {
                    'sku': sku,
                    'stock_status': 'Unknown',
                    'price': None,
                    'product_name': None,
                    'product_url': product_url
                }
            
            soup = self.parse_html(html_content)
            
            # Extract information using store config
            product_name = self.extract_name(soup, store_config)
            price = self.extract_price_generic(soup, store_config)
            stock_status = self.extract_stock_status(soup, store_config)
            
            return {
                'sku': sku,
                'stock_status': stock_status,
                'price': price,
                'product_name': product_name,
                'product_url': product_url,
                'store': store_config['name']
            }
            
        except Exception as e:
            self.logger.error("Error checking %s for SKU %s: %s", store_config['name'], sku, e)
            return {
                'sku': sku,
                'stock_status': 'Unknown',
                'price': None,
                'product_name': None,
                'product_url': product_url
            }

    async def find_product_url(self, store_config: Dict, sku: str) -> Optional[str]:
        """Find product URL by searching or using URL pattern"""
        try:
            # Try search first
            search_url = store_config['search_url'].format(query=sku)
            html_content = await self.safe_request(search_url)
            
            if html_content:
                soup = self.parse_html(html_content)
                
                # Look for product links containing the SKU
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    
                    # Check if URL matches the store's SKU pattern
                    pattern = store_config['sku_url_pattern'].format(sku=sku)
                    if re.search(pattern.replace('{sku}', sku), href):
                        if not href.startswith('http'):
                            href = store_config['base_url'] + href
                        return href
            
            return None
            
        except Exception as e:
            self.logger.error("Error finding product URL: %s", e)
            return None

    def extract_name(self, soup: BeautifulSoup, store_config: Dict) -> Optional[str]:
        """Extract product name using store config"""
        try:
            name_element = soup.select_one(store_config['name_selector'])
            return name_element.get_text(strip=True) if name_element else None
        except Exception:
            return None

    def extract_price_generic(self, soup: BeautifulSoup, store_config: Dict) -> Optional[float]:
        """Extract price using store config selectors"""
        try:
            for selector in store_config['price_selectors']:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    extracted_price = self.extract_price(price_text)
                    if extracted_price:
                        return extracted_price
            return None
        except Exception:
            return None

    def extract_stock_status(self, soup: BeautifulSoup, store_config: Dict) -> str:
        """Extract stock status using store config indicators"""
        try:
            page_text = soup.get_text().lower()
            
            # Check each status type
            for status, indicators in store_config['stock_indicators'].items():
                for indicator in indicators:
                    if indicator.lower() in page_text:
                        return self.normalize_status(status)
            
            return 'Unknown'
            
        except Exception:
            return 'Unknown'

    def normalize_status(self, status: str) -> str:
        """Normalize status names"""
        status_map = {
            'in_stock': 'In Stock',
            'out_of_stock': 'Out of Stock',
            'preorder': 'Pre-order'
        }
        return status_map.get(status, 'Unknown')

    def detect_store_from_url(self, url: str) -> Optional[str]:
        """Detect which store based on URL"""
        for store_name, config in self.store_configs.items():
            if config['base_url'].replace('https://', '').replace('http://', '') in url:
                return store_name
        return None

    def get_product_url(self, sku: str) -> str:
        """Get generic search URL for SKU"""
        # Default to EB Games NZ for now
        return f"https://www.ebgames.co.nz/search?q={sku}"
    
    async def parse_nova_games_products(self, html: str, base_url: str) -> List[Dict]:
        """Parse Nova Games product listing page"""
        products = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Nova Games: Find product cards with proper names
            # Look for product containers with both image and text
            product_containers = soup.find_all('div', class_=lambda x: x and any(
                cls in str(x).lower() for cls in ['product', 'item', 'card']
            ))
            
            if not product_containers:
                # Fallback: Look for direct product links with text
                product_links = soup.find_all('a', href=lambda x: x and '/products/' in x)
                product_containers = [link for link in product_links 
                                    if link.get_text(strip=True) and len(link.get_text(strip=True)) > 5]
            
            logger.info(f"Found {len(product_containers)} potential products on Nova Games")
            
            seen_products = set()  # To avoid duplicates
            
            for container in product_containers:
                try:
                    # Find the product link within this container
                    if container.name == 'a':
                        link = container
                    else:
                        link = container.find('a', href=lambda x: x and '/products/' in x)
                    
                    if not link:
                        continue
                    
                    # Product URL
                    href = link.get('href', '')
                    if not href or href in seen_products:
                        continue
                        
                    # Skip image-only links
                    if 'cdn/shop' in href or '/files/' in href:
                        continue
                        
                    seen_products.add(href)
                    product_url = f"{base_url}{href}" if href.startswith('/') else href
                    
                    # Extract SKU from URL
                    sku = href.split('/')[-1] if '/' in href else ''
                    
                    # Get product name - try multiple approaches
                    name = None
                    
                    # Method 1: Look for product title in container
                    title_elem = container.find(['h2', 'h3', 'h4', 'span', 'div'], 
                                              class_=lambda x: x and 'title' in str(x).lower())
                    if title_elem:
                        name = title_elem.get_text(strip=True)
                    
                    # Method 2: Link text if no title found
                    if not name or len(name) < 5:
                        name = link.get_text(strip=True)
                    
                    # Method 3: Look for any text in the container
                    if not name or len(name) < 5:
                        text_elements = container.find_all(text=True)
                        for text in text_elements:
                            text = text.strip()
                            if len(text) > 10 and not text.lower().startswith(('$', 'add', 'buy', 'sale')):
                                name = text
                                break
                    
                    # Skip if still no good name
                    if not name or len(name) < 5:
                        continue
                    
                    # Only include Pokemon-related products
                    if not any(keyword.lower() in name.lower() for keyword in 
                              ['pokemon', 'pokémon', 'tcg', 'trading card', 'trainer', 'battle deck', 'booster']):
                        continue
                    
                    # Try to find price (it might be in a sibling element)
                    price = 0.0
                    price_element = link.find_next('span', class_='price') or \
                                   link.find_next('span', class_='money') or \
                                   link.parent.find('span', class_='price') if link.parent else None
                    
                    if price_element:
                        price_text = price_element.get_text(strip=True)
                        extracted_price = self.extract_price(price_text)
                        if extracted_price:
                            price = extracted_price
                    
                    products.append({
                        'name': name,
                        'price': price,
                        'url': product_url,
                        'sku': sku,
                        'store': 'Nova Games NZ',
                        'status': 'In Stock'  # Nova Games only shows in-stock items
                    })
                    
                except Exception as e:
                    logger.warning(f"Error parsing Nova Games product link: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing Nova Games HTML: {e}")
        
        logger.info(f"Parsed {len(products)} Pokemon products from Nova Games")
        return products

    async def parse_ebgames_products(self, html: str, base_url: str) -> List[Dict]:
        """Parse EB Games product listing page"""
        products = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # EB Games: Find product links in search results
            # Look for product links that match the pattern /product/toys-and-collectibles/XXXXX-
            product_links = soup.find_all('a', href=lambda x: x and '/product/' in x and 'toys' in x)
            
            if not product_links:
                # Fallback: Look for any product links
                product_links = soup.find_all('a', href=lambda x: x and '/product/' in x)
            
            logger.info(f"Found {len(product_links)} potential EB Games products")
            
            seen_skus = set()  # To avoid duplicates
            
            for link in product_links:
                try:
                    href = link.get('href', '')
                    if not href:
                        continue
                    
                    # Extract SKU from URL: /product/toys-and-collectibles/331128-pokemon-tcg...
                    import re
                    sku_match = re.search(r'/product/[^/]+/(\d+)-', href)
                    if not sku_match:
                        continue
                        
                    sku = sku_match.group(1)
                    if sku in seen_skus:
                        continue
                    seen_skus.add(sku)
                    
                    # Build full product URL
                    product_url = f"{base_url}{href}" if href.startswith('/') else href
                    
                    # Get product name from link text or find in container
                    name = link.get_text(strip=True)
                    
                    # If name is too short, look in the parent container
                    if not name or len(name) < 10:
                        container = link.find_parent(['div', 'article', 'li'])
                        if container:
                            # Look for title elements
                            title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'span'], 
                                                      class_=lambda x: x and 'title' in str(x).lower())
                            if title_elem:
                                name = title_elem.get_text(strip=True)
                    
                    # Skip if still no good name
                    if not name or len(name) < 5:
                        continue
                    
                    # Only include Pokemon-related products
                    if not any(keyword.lower() in name.lower() for keyword in 
                              ['pokemon', 'pokémon', 'tcg', 'trading card', 'trainer']):
                        continue
                    
                    # Try to find price in the same container
                    price = 0.0
                    container = link.find_parent(['div', 'article', 'li'])
                    if container:
                        price_elem = container.find('span', {'itemprop': 'price'}) or \
                                   container.find('span', class_='price') or \
                                   container.find(['span', 'div'], class_=lambda x: x and 'price' in str(x).lower())
                        
                        if price_elem:
                            price_text = price_elem.get('content') or price_elem.get_text(strip=True)
                            extracted_price = self.extract_price(price_text)
                            if extracted_price:
                                price = extracted_price
                    
                    products.append({
                        'name': name,
                        'price': price,
                        'url': product_url,
                        'sku': sku,
                        'store': 'EB Games NZ',
                        'status': 'In Stock'  # If it appears in search, it's available
                    })
                    
                except Exception as e:
                    logger.warning(f"Error parsing EB Games product link: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing EB Games HTML: {e}")
        
        logger.info(f"Parsed {len(products)} Pokemon products from EB Games")
        return products

    async def parse_cardmerchant_products(self, json_data: str, base_url: str) -> List[Dict]:
        """Parse Card Merchant JSON product data"""
        products = []
        
        try:
            import json
            data = json.loads(json_data)
            
            # Extract products from JSON response
            product_list = data.get('products', [])
            
            logger.info(f"Found {len(product_list)} Card Merchant products in JSON")
            
            for product in product_list:
                try:
                    # Extract basic product info
                    title = product.get('title', '')
                    handle = product.get('handle', '')
                    product_id = product.get('id', '')
                    
                    if not title or not handle:
                        continue
                    
                    # Build product URL
                    product_url = f"{base_url}/collections/pokemon-sealed/products/{handle}"
                    
                    # Get price from first available variant
                    variants = product.get('variants', [])
                    price = 0.0
                    available = False
                    
                    for variant in variants:
                        if variant.get('available', False):
                            available = True
                            variant_price = variant.get('price', 0)
                            # Card Merchant prices are already in dollars (not cents like most Shopify stores)
                            price = float(variant_price) if variant_price else 0.0
                            break
                    
                    # Only include available products (Card Merchant only shows in-stock)
                    if not available:
                        continue
                    
                    products.append({
                        'name': title,
                        'price': price,
                        'url': product_url,
                        'sku': handle,  # Use handle as SKU
                        'store': 'Card Merchant NZ',
                        'status': 'In Stock'
                    })
                    
                except Exception as e:
                    logger.warning(f"Error parsing Card Merchant product: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing Card Merchant JSON: {e}")
        
        logger.info(f"Parsed {len(products)} Pokemon products from Card Merchant")
        return products

    def parse_ebgames_products_selenium(self) -> List[Dict]:
        """Parse EB Games NZ products using Selenium to bypass bot detection"""
        products = []
        
        try:
            # Import Selenium here to avoid dependency issues if not installed
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException
            import time
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Get EB Games Pokemon search page
            pokemon_url = "https://www.ebgames.co.nz/search?q=pokemon"
            logger.info(f"Selenium accessing: {pokemon_url}")
            
            driver.get(pokemon_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for content to load
            time.sleep(3)
            
            # Scroll to load all products (simple scroll)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Get page HTML
            page_html = driver.page_source
            driver.quit()
            
            # Parse with BeautifulSoup
            page_soup = BeautifulSoup(page_html, "html.parser")
            containers = page_soup.select("div[class*='product']")
            
            logger.info(f"Found {len(containers)} potential EB Games products")
            
            for container in containers:
                try:
                    # Extract product name
                    name_element = container.select_one("h3 a, h2 a, .product-title a")
                    if not name_element:
                        continue
                    
                    product_name = name_element.get_text(strip=True)
                    
                    # Filter Pokemon products
                    if not self.is_pokemon_tcg_product(product_name):
                        continue
                    
                    # Get product URL
                    href = name_element.get('href', '')
                    if href.startswith('/'):
                        product_url = f"https://www.ebgames.co.nz{href}"
                    else:
                        product_url = href
                    
                    # Extract price
                    price = 0.0
                    price_element = container.select_one(".price, [class*='price']")
                    if price_element:
                        price_text = price_element.get_text()
                        import re
                        price_match = re.search(r'\$([0-9]+\.?[0-9]*)', price_text.replace(',', ''))
                        if price_match:
                            price = float(price_match.group(1))
                    
                    # Determine stock status
                    container_text = container.get_text().lower()
                    if 'out of stock' in container_text:
                        status = 'Out of Stock'
                    elif 'preorder' in container_text or 'pre-order' in container_text:
                        status = 'Pre-order'
                    else:
                        status = 'In Stock'
                    
                    # Extract SKU from URL
                    sku = ''
                    sku_match = re.search(r'/([0-9]+)-', product_url)
                    if sku_match:
                        sku = sku_match.group(1)
                    
                    products.append({
                        'name': product_name,
                        'price': price,
                        'url': product_url,
                        'sku': sku,
                        'store': 'EB Games NZ',
                        'status': status
                    })
                    
                except Exception as e:
                    logger.warning(f"Error parsing EB Games product: {e}")
                    continue
            
        except ImportError:
            logger.error("Selenium not installed - cannot scrape EB Games")
        except Exception as e:
            logger.error(f"Error scraping EB Games with Selenium: {e}")
            if 'driver' in locals():
                try:
                    driver.quit()
                except:
                    pass
        
        logger.info(f"Parsed {len(products)} Pokemon TCG products from EB Games")
        return products

    def is_pokemon_tcg_product(self, product_name: str) -> bool:
        """Check if product is Pokemon TCG related (excluding games and merchandise)"""
        name_lower = product_name.lower()
        
        # Include TCG-specific keywords
        tcg_keywords = [
            'tcg', 'trading card', 'booster', 'deck', 'collection',
            'premium', 'tin', 'box', 'pack', 'elite trainer'
        ]
        
        # Exclude non-TCG products
        exclude_keywords = [
            'nintendo switch', 'game', 'plush', 'towel', 'tumbler', 
            'clothing', 'figure', 'toy', 'dvd', 'bluray'
        ]
        
        # Must contain Pokemon
        if 'pokemon' not in name_lower and 'pokémon' not in name_lower:
            return False
        
        # Exclude non-TCG items
        if any(keyword in name_lower for keyword in exclude_keywords):
            return False
        
        # Include if has TCG keywords
        return any(keyword in name_lower for keyword in tcg_keywords)

    async def get_nova_games_products(self) -> List[Dict[str, Any]]:
        """Get current Pokemon products from Nova Games NZ"""
        try:
            import aiohttp
            
            url = "https://novagames.co.nz/collections/pokemon"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        html = await response.text()
                        products = await self.parse_nova_games_products(html, "https://novagames.co.nz")
                        return [
                            {
                                'name': p['name'],
                                'price': p.get('price', 0.0),
                                'url': p['url'],
                                'sku': p.get('sku', ''),
                                'available': p.get('status', '') == 'In Stock'
                            }
                            for p in products
                        ]
                    else:
                        logger.error(f"Nova Games returned status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting Nova Games products: {e}")
            return []

    async def get_cardmerchant_products(self) -> List[Dict[str, Any]]:
        """Get current Pokemon products from Card Merchant NZ"""
        try:
            import aiohttp
            
            url = "https://cardmerchant.co.nz/products.json"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        json_text = await response.text()
                        products = await self.parse_cardmerchant_products(json_text, "https://cardmerchant.co.nz")
                        return [
                            {
                                'name': p['name'],
                                'price': p.get('price', 0.0),
                                'url': p['url'],
                                'sku': p.get('sku', ''),
                                'available': p.get('status', '') == 'In Stock'
                            }
                            for p in products
                        ]
                    else:
                        logger.error(f"Card Merchant returned status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting Card Merchant products: {e}")
            return []

    async def get_ebgames_products(self) -> List[Dict[str, Any]]:
        """Get current Pokemon TCG products from EB Games NZ using Selenium"""
        try:
            # Run Selenium in a thread to avoid blocking
            import asyncio
            import concurrent.futures
            
            def run_selenium():
                return self.parse_ebgames_products_selenium()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                products = await asyncio.get_event_loop().run_in_executor(
                    executor, run_selenium
                )
            
            return [
                {
                    'name': p['name'],
                    'price': p.get('price', 0.0),
                    'url': p['url'],
                    'sku': p.get('sku', ''),
                    'available': p.get('status', '') == 'In Stock'
                }
                for p in products
            ]
        except Exception as e:
            logger.error(f"Error getting Card Merchant products: {e}")
            return []

    async def get_ebgames_products_selenium(self) -> List[Dict[str, Any]]:
        """Get Pokemon TCG products from EB Games NZ using Selenium"""
        try:
            from universal_selenium_scraper import get_ebgames_pokemon_tcg
            products = await get_ebgames_pokemon_tcg()
            return [
                {
                    'name': p['name'],
                    'price': p.get('price', 0.0),
                    'url': p.get('url', ''),
                    'sku': p.get('sku', ''),
                    'available': p.get('status', '') == 'In Stock'
                }
                for p in products
            ]
        except Exception as e:
            logger.error(f"Error getting EB Games products with Selenium: {e}")
            return []

    async def get_warehouse_products_selenium(self) -> List[Dict[str, Any]]:
        """Get Pokemon TCG products from The Warehouse NZ using Selenium"""
        try:
            from universal_selenium_scraper import get_warehouse_pokemon_tcg
            products = await get_warehouse_pokemon_tcg()
            return [
                {
                    'name': p['name'],
                    'price': p.get('price', 0.0),
                    'url': p.get('url', ''),
                    'sku': p.get('sku', ''),
                    'available': p.get('status', '') == 'In Stock'
                }
                for p in products
            ]
        except Exception as e:
            logger.error(f"Error getting Warehouse products with Selenium: {e}")
            return []

    async def get_jbhifi_products_selenium(self) -> List[Dict[str, Any]]:
        """Get Pokemon TCG products from JB Hi-Fi NZ using Selenium"""
        try:
            from universal_selenium_scraper import get_jbhifi_pokemon_tcg
            products = await get_jbhifi_pokemon_tcg()
            return [
                {
                    'name': p['name'],
                    'price': p.get('price', 0.0),
                    'url': p.get('url', ''),
                    'sku': p.get('sku', ''),
                    'available': p.get('status', '') == 'In Stock'
                }
                for p in products
            ]
        except Exception as e:
            logger.error(f"Error getting JB Hi-Fi products with Selenium: {e}")
            return []

    async def get_kmart_products_selenium(self) -> List[Dict[str, Any]]:
        """Get Pokemon TCG products from Kmart NZ using Selenium"""
        try:
            from universal_selenium_scraper import get_kmart_pokemon_tcg
            products = await get_kmart_pokemon_tcg()
            return [
                {
                    'name': p['name'],
                    'price': p.get('price', 0.0),
                    'url': p.get('url', ''),
                    'sku': p.get('sku', ''),
                    'available': p.get('status', '') == 'In Stock'
                }
                for p in products
            ]
        except Exception as e:
            logger.error(f"Error getting Kmart products with Selenium: {e}")
            return []

    async def get_mightyape_products_selenium(self) -> List[Dict[str, Any]]:
        """Get Pokemon TCG products from Mighty Ape NZ using Selenium"""
        try:
            from universal_selenium_scraper import get_mightyape_pokemon_tcg
            products = await get_mightyape_pokemon_tcg()
            return [
                {
                    'name': p['name'],
                    'price': p.get('price', 0.0),
                    'url': p.get('url', ''),
                    'sku': p.get('sku', ''),
                    'available': p.get('status', '') == 'In Stock'
                }
                for p in products
            ]
        except Exception as e:
            logger.error(f"Error getting Mighty Ape products with Selenium: {e}")
            return []

    def add_custom_store(self, store_name: str, store_config: Dict):
        """Add a custom store configuration at runtime"""
        self.store_configs[store_name] = store_config
        self.logger.info("Added custom store: %s", store_name)

    def list_supported_stores(self) -> List[str]:
        """Get list of all supported stores"""
        return [config['name'] for config in self.store_configs.values()]