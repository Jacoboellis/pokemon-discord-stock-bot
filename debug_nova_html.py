#!/usr/bin/env python3
"""
Debug Nova Games HTML structure
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def debug_nova_games_html():
    """Debug the actual HTML structure of Nova Games"""
    url = "https://novagames.co.nz/collections/pokemon"
    
    async with aiohttp.ClientSession() as session:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                print(f"✅ Successfully fetched Nova Games HTML ({len(html)} chars)")
                print()
                
                # Try different selectors to find products
                selectors_to_try = [
                    'div.product-item',
                    'div.product-card', 
                    'div.grid-item',
                    'article.product-item',
                    'div[class*="product"]',
                    'article[class*="product"]',
                    '.product',
                    'a[href*="/products/"]'
                ]
                
                for selector in selectors_to_try:
                    elements = soup.select(selector)
                    print(f"Selector '{selector}': {len(elements)} elements found")
                    if len(elements) > 0:
                        # Show first element structure
                        first_element = elements[0]
                        print(f"  First element tag: {first_element.name}")
                        print(f"  First element classes: {first_element.get('class', [])}")
                        print(f"  First element text (truncated): {first_element.get_text(strip=True)[:100]}...")
                        print()
                
                # Look for product links
                product_links = soup.find_all('a', href=lambda x: x and '/products/' in x)
                print(f"Links with /products/: {len(product_links)} found")
                
                if product_links:
                    print("First 5 product links:")
                    for i, link in enumerate(product_links[:5], 1):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        print(f"  {i}. {text[:50]}... -> {href}")
                    print()
                
                # Save a sample of HTML for inspection
                with open('nova_games_sample.html', 'w', encoding='utf-8') as f:
                    f.write(html[:10000])  # First 10k chars
                print("💾 Saved first 10k chars to nova_games_sample.html for inspection")
                
            else:
                print(f"❌ HTTP {response.status}")

if __name__ == "__main__":
    asyncio.run(debug_nova_games_html())