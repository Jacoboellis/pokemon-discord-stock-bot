#!/usr/bin/env python3
"""
EB Games New Zealand monitor for Pokemon stock tracking
"""

import re
import asyncio
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from .base_monitor import BaseMonitor


class EBGamesNZMonitor(BaseMonitor):
    """Monitor for EB Games New Zealand Pokemon products"""
    
    def __init__(self, config):
        super().__init__(config)
        self.store_name = "EB Games NZ"
        self.base_url = "https://www.ebgames.co.nz"
        self.search_url = "https://www.ebgames.co.nz/search?q=pokemon+tcg"

    async def check_stock(self, sku: str, product_url: str = None) -> Dict[str, Any]:
        """Check stock for a specific SKU"""
        try:
            # If no product URL provided, try to find it
            if not product_url:
                product_url = await self.find_product_url(sku)
                if not product_url:
                    return {
                        'sku': sku,
                        'stock_status': 'Unknown',
                        'price': None,
                        'product_name': None,
                        'product_url': None
                    }
            
            # Get the product page
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
            
            # Extract product information
            product_data = self.extract_product_info(soup, sku, product_url)
            return product_data
            
        except Exception as e:
            self.logger.error("Error checking EB Games NZ stock for SKU %s: %s", sku, e)
            return {
                'sku': sku,
                'stock_status': 'Unknown',
                'price': None,
                'product_name': None,
                'product_url': product_url
            }

    def get_product_url(self, sku: str) -> str:
        """Generate product URL for SKU"""
        # EB Games NZ doesn't have a direct SKU->URL mapping
        # We need to search for the product
        return f"https://www.ebgames.co.nz/search?q={sku}"

    async def find_product_url(self, sku: str) -> Optional[str]:
        """Find the actual product URL for a given SKU"""
        try:
            search_url = f"https://www.ebgames.co.nz/search?q={sku}"
            html_content = await self.safe_request(search_url)
            
            if not html_content:
                return None
                
            soup = self.parse_html(html_content)
            
            # Find product links that contain the SKU
            product_links = soup.find_all('a', href=True)
            for link in product_links:
                href = link.get('href', '')
                if f'/{sku}-' in href:
                    if not href.startswith('http'):
                        href = self.base_url + href
                    return href
            
            return None
            
        except Exception as e:
            self.logger.error("Error finding product URL for SKU %s: %s", sku, e)
            return None

    def extract_product_info(self, soup: BeautifulSoup, sku: str, product_url: str) -> Dict[str, Any]:
        """Extract product information from the product page"""
        try:
            # Get product name from h1 tag
            name_element = soup.find('h1')
            product_name = name_element.get_text(strip=True) if name_element else None
            
            # Extract price
            price = self.extract_product_price(soup)
            
            # Check availability
            availability = self.check_availability_status(soup)
            
            return {
                'sku': sku,
                'stock_status': availability,
                'price': price,
                'product_name': product_name,
                'product_url': product_url
            }
            
        except Exception as e:
            self.logger.error("Error extracting product info: %s", e)
            return {
                'sku': sku,
                'stock_status': 'Unknown',
                'price': None,
                'product_name': None,
                'product_url': product_url
            }

    def extract_product_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from product page"""
        try:
            # Look for price in various possible locations
            price_selectors = [
                'span.price',
                '.price-current',
                '.current-price',
                '[class*="price"]'
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    return self.extract_price(price_text)
            
            # Look for price in text content (fallback)
            price_text_element = soup.find(string=re.compile(r'\$\d+\.\d{2}'))
            if price_text_element:
                return self.extract_price(price_text_element)
            
            return None
            
        except Exception as e:
            self.logger.error("Error extracting price: %s", e)
            return None

    def check_availability_status(self, soup: BeautifulSoup) -> str:
        """Check product availability status"""
        try:
            # Get all text content
            page_text = soup.get_text().lower()
            
            # Check for availability indicators
            if 'add to cart' in page_text:
                return 'In Stock'
            elif any(phrase in page_text for phrase in ['out of stock', 'sold out', 'unavailable']):
                return 'Out of Stock'
            elif any(phrase in page_text for phrase in ['preorder', 'pre-order']):
                return 'Pre-order'
            elif 'coming soon' in page_text:
                return 'Coming Soon'
            else:
                # Look for specific button states
                add_to_cart_btn = soup.find('button', string=re.compile(r'add to cart', re.IGNORECASE))
                if add_to_cart_btn and not add_to_cart_btn.get('disabled'):
                    return 'In Stock'
                
                return 'Unknown'
                
        except Exception as e:
            self.logger.error("Error checking availability: %s", e)
            return 'Unknown'

    async def search_pokemon_products(self) -> list:
        """Search for all Pokemon TCG products"""
        try:
            self.logger.info("Searching for Pokemon TCG products on EB Games NZ...")
            
            html_content = await self.safe_request(self.search_url)
            if not html_content:
                return []
            
            soup = self.parse_html(html_content)
            
            # Find all product links
            product_links = []
            view_product_links = soup.find_all('a', href=True)
            
            for link in view_product_links:
                href = link.get('href', '')
                if '/product/' in href and 'pokemon' in href.lower():
                    if not href.startswith('http'):
                        href = self.base_url + href
                    
                    # Extract SKU from URL
                    sku_match = re.search(r'/(\d+)-', href)
                    if sku_match:
                        sku = sku_match.group(1)
                        product_links.append({
                            'sku': sku,
                            'url': href
                        })
            
            # Remove duplicates
            unique_products = {}
            for product in product_links:
                unique_products[product['sku']] = product
            
            self.logger.info("Found %d unique Pokemon products on EB Games NZ", len(unique_products))
            
            return list(unique_products.values())
            
        except Exception as e:
            self.logger.error("Error searching Pokemon products: %s", e)
            return []

    def is_pokemon_product(self, product_name: str) -> bool:
        """Check if product is Pokemon-related"""
        if not product_name:
            return False
            
        pokemon_keywords = [
            'pokemon', 'tcg', 'trading card', 'booster', 'pack',
            'pikachu', 'charizard', 'deck', 'collection'
        ]
        
        name_lower = product_name.lower()
        return any(keyword in name_lower for keyword in pokemon_keywords)