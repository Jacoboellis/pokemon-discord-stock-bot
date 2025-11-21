#!/usr/bin/env python3
"""Simple HTTP scraper for Nova Games and Card Merchant - no Selenium needed"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

class SimpleHTTPScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    async def scrape_nova_games(self):
        """Scrape Nova Games NZ - https://novagames.co.nz/collections/pokemon"""
        url = "https://novagames.co.nz/collections/pokemon"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        products = []
                        
                        # Nova Games uses product cards
                        product_cards = soup.find_all(['div', 'article'], class_=re.compile(r'product|item|card'))
                        
                        for card in product_cards:
                            try:
                                # Extract name
                                name_elem = card.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|name|product'))
                                if not name_elem:
                                    name_elem = card.find('a')
                                
                                name = name_elem.get_text().strip() if name_elem else "Unknown Product"
                                
                                # Extract price
                                price_elem = card.find(class_=re.compile(r'price|cost|amount'))
                                if price_elem:
                                    price_text = price_elem.get_text().strip()
                                    price_match = re.search(r'[\$]?(\d+\.?\d*)', price_text.replace(',', ''))
                                    price = float(price_match.group(1)) if price_match else 0.0
                                else:
                                    price = 0.0
                                
                                # Extract URL
                                link_elem = card.find('a')
                                url = f"https://novagames.co.nz{link_elem['href']}" if link_elem and link_elem.get('href') else ""
                                
                                # Only include Pokemon products
                                if any(keyword in name.lower() for keyword in ['pokemon', 'tcg', 'booster', 'pack']):
                                    products.append({
                                        'name': name,
                                        'price': price,
                                        'url': url,
                                        'store': 'Nova Games NZ',
                                        'stock_status': 'In Stock'  # Nova only shows in-stock items
                                    })
                                    
                            except Exception as e:
                                print(f"Error parsing Nova Games product: {e}")
                                continue
                        
                        return products
                        
                    else:
                        print(f"Nova Games returned status {response.status}")
                        return []
                        
            except Exception as e:
                print(f"Error scraping Nova Games: {e}")
                return []

    async def scrape_card_merchant(self):
        """Scrape Card Merchant NZ - https://cardmerchant.co.nz/collections/pokemon-sealed"""
        url = "https://cardmerchant.co.nz/collections/pokemon-sealed"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        products = []
                        
                        # Card Merchant uses product grid items
                        product_items = soup.find_all(['div', 'article'], class_=re.compile(r'product|grid|item'))
                        
                        for item in product_items:
                            try:
                                # Extract name
                                name_elem = item.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|name|product'))
                                if not name_elem:
                                    name_elem = item.find('a')
                                
                                name = name_elem.get_text().strip() if name_elem else "Unknown Product"
                                
                                # Extract price
                                price_elem = item.find(class_=re.compile(r'price|cost|amount|money'))
                                if price_elem:
                                    price_text = price_elem.get_text().strip()
                                    price_match = re.search(r'[\$]?(\d+\.?\d*)', price_text.replace(',', ''))
                                    price = float(price_match.group(1)) if price_match else 0.0
                                else:
                                    price = 0.0
                                
                                # Extract URL
                                link_elem = item.find('a')
                                url = f"https://cardmerchant.co.nz{link_elem['href']}" if link_elem and link_elem.get('href') else ""
                                
                                # Check stock status
                                stock_elem = item.find(class_=re.compile(r'stock|inventory|available'))
                                if stock_elem and 'out' in stock_elem.get_text().lower():
                                    stock_status = 'Out of Stock'
                                else:
                                    stock_status = 'In Stock'
                                
                                if name != "Unknown Product":
                                    products.append({
                                        'name': name,
                                        'price': price,
                                        'url': url,
                                        'store': 'Card Merchant NZ',
                                        'stock_status': stock_status
                                    })
                                    
                            except Exception as e:
                                print(f"Error parsing Card Merchant product: {e}")
                                continue
                        
                        return products
                        
                    else:
                        print(f"Card Merchant returned status {response.status}")
                        return []
                        
            except Exception as e:
                print(f"Error scraping Card Merchant: {e}")
                return []

async def test_simple_scrapers():
    """Test both stores with simple HTTP requests"""
    scraper = SimpleHTTPScraper()
    
    print("🔍 === Testing Nova Games NZ (Simple HTTP) ===")
    nova_products = await scraper.scrape_nova_games()
    
    if nova_products:
        print(f"✅ Found {len(nova_products)} products at Nova Games!")
        for i, product in enumerate(nova_products[:5], 1):
            print(f"  {i}. {product['name'][:60]}... - ${product['price']}")
    else:
        print("⚠️ No products found at Nova Games")
    
    print(f"\n🔍 === Testing Card Merchant NZ (Simple HTTP) ===")
    card_products = await scraper.scrape_card_merchant()
    
    if card_products:
        print(f"✅ Found {len(card_products)} products at Card Merchant!")
        for i, product in enumerate(card_products[:5], 1):
            print(f"  {i}. {product['name'][:60]}... - ${product['price']} ({product['stock_status']})")
    else:
        print("⚠️ No products found at Card Merchant")
    
    total_products = len(nova_products) + len(card_products)
    print(f"\n🎯 Total products found: {total_products}")
    
    return nova_products + card_products

if __name__ == "__main__":
    products = asyncio.run(test_simple_scrapers())