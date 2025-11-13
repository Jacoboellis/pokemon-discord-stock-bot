#!/usr/bin/env python3
"""Research script for EB Games NZ"""
import aiohttp
import asyncio
from bs4 import BeautifulSoup

async def research_ebgames():
    url = "https://www.ebgames.co.nz/search?category=toys-hobbies&subcategory=toys-hobbies-trading-cards&attributes=franchise%3Apokemon"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            print(f'Testing EB Games: {url}')
            async with session.get(url, headers=headers, timeout=15) as response:
                print(f'Status: {response.status}')
                print(f'Headers: {dict(response.headers)}')
                
                if response.status == 200:
                    html = await response.text()
                    print(f'✅ SUCCESS - Content length: {len(html)} chars')
                    
                    # Parse HTML to find product structure
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for common product selectors
                    product_containers = []
                    
                    # Try different product container patterns
                    patterns = [
                        {'selector': '[class*="product"]', 'desc': 'Product classes'},
                        {'selector': '[class*="item"]', 'desc': 'Item classes'},
                        {'selector': '[class*="card"]', 'desc': 'Card classes'},
                        {'selector': 'article', 'desc': 'Article tags'},
                        {'selector': '[data-product]', 'desc': 'Data product attributes'},
                        {'selector': '.tile', 'desc': 'Tile classes'},
                        {'selector': '.grid-item', 'desc': 'Grid item classes'}
                    ]
                    
                    for pattern in patterns:
                        elements = soup.select(pattern['selector'])
                        if elements:
                            print(f'Found {len(elements)} elements with {pattern["desc"]}')
                            product_containers.extend(elements[:3])  # Take first 3 for analysis
                    
                    # Analyze first few product containers
                    print(f'\n=== ANALYZING PRODUCT STRUCTURE ===')
                    for i, container in enumerate(product_containers[:3]):
                        print(f'\nProduct {i+1}:')
                        
                        # Look for product links
                        links = container.find_all('a', href=True)
                        for link in links[:2]:
                            href = link.get('href')
                            text = link.get_text(strip=True)
                            if text and len(text) > 5:
                                print(f'  Link: {text[:50]} -> {href[:50]}')
                        
                        # Look for prices
                        price_elements = container.find_all(['span', 'div'], class_=lambda x: x and 'price' in str(x).lower())
                        for price in price_elements:
                            print(f'  Price: {price.get_text(strip=True)}')
                        
                        # Look for titles
                        titles = container.find_all(['h1', 'h2', 'h3', 'h4'])
                        for title in titles:
                            text = title.get_text(strip=True)
                            if text:
                                print(f'  Title: {text[:50]}')
                    
                    # Save HTML sample for analysis
                    with open('ebgames_sample.html', 'w', encoding='utf-8') as f:
                        f.write(html[:10000])  # First 10k chars
                    print(f'\n📄 Saved HTML sample to ebgames_sample.html')
                    
                elif response.status == 403:
                    print(f'❌ 403 FORBIDDEN - EB Games is blocking bots')
                    print('This means we need to use more sophisticated headers/techniques')
                else:
                    print(f'❌ Status {response.status}')
                    
        except Exception as e:
            print(f'❌ Error: {e}')

if __name__ == "__main__":
    asyncio.run(research_ebgames())