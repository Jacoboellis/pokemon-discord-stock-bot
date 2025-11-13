#!/usr/bin/env python3
"""
Debug Nova Games product structure specifically
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def debug_nova_products():
    """Debug the actual product structure of Nova Games"""
    url = "https://novagames.co.nz/collections/pokemon"
    
    async with aiohttp.ClientSession() as session:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                print(f"✅ Successfully fetched Nova Games HTML")
                print()
                
                # Find product links
                product_links = soup.find_all('a', href=lambda x: x and '/products/' in x)
                print(f"Found {len(product_links)} product links")
                print()
                
                # Analyze each product link
                for i, link in enumerate(product_links[:10], 1):  # First 10
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    parent = link.parent
                    
                    print(f"Product Link {i}:")
                    print(f"  URL: {href}")
                    print(f"  Text: {text[:100]}...")
                    print(f"  Parent tag: {parent.name if parent else 'None'}")
                    print(f"  Parent classes: {parent.get('class', []) if parent else []}")
                    
                    # Try to find price in parent or nearby elements
                    price_found = False
                    for price_selector in ['.price', '[class*="price"]', '.money', '[class*="money"]']:
                        price_elem = parent.select_one(price_selector) if parent else None
                        if price_elem:
                            print(f"  Price ({price_selector}): {price_elem.get_text(strip=True)}")
                            price_found = True
                            break
                    
                    if not price_found:
                        print(f"  Price: Not found")
                    
                    print(f"  Full parent HTML: {str(parent)[:200] if parent else 'None'}...")
                    print()
                
            else:
                print(f"❌ HTTP {response.status}")

if __name__ == "__main__":
    asyncio.run(debug_nova_products())