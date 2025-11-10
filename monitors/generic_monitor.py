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
                'search_url': 'https://www.ebgames.co.nz/search?q={query}',
                'sku_url_pattern': '/product/[^/]+/{sku}-',  # /product/toys-and-collectibles/331696-
                'price_selectors': ['span.price', '.price-current', '[class*="price"]'],
                'name_selector': 'h1',
                'stock_indicators': {
                    'in_stock': ['add to cart'],
                    'out_of_stock': ['out of stock', 'sold out'],
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

    async def add_custom_store(self, store_name: str, store_config: Dict):
        """Add a custom store configuration at runtime"""
        self.store_configs[store_name] = store_config
        self.logger.info("Added custom store: %s", store_name)

    def list_supported_stores(self) -> List[str]:
        """Get list of all supported stores"""
        return [config['name'] for config in self.store_configs.values()]