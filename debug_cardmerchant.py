#!/usr/bin/env python3
"""Debug Card Merchant HTML structure"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def debug_cardmerchant():
    url = "https://cardmerchant.co.nz/collections/pokemon-sealed"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    print(f"✅ Connected to Card Merchant successfully")
                    print(f"   Content length: {len(html)} chars")
                    
                    # Look for product links
                    product_links = soup.find_all('a', href=lambda x: x and '/products/' in x)
                    print(f"   Found {len(product_links)} product links")
                    
                    # Analyze first few products
                    print(f"\n=== ANALYZING FIRST 3 PRODUCTS ===")
                    for i, link in enumerate(product_links[:3]):
                        print(f"\nProduct {i+1}:")
                        href = link.get('href', '')
                        print(f"  URL: {href}")
                        
                        # Get link text
                        link_text = link.get_text(strip=True)
                        print(f"  Link Text: '{link_text}'")
                        
                        # Look in parent container
                        container = link.find_parent(['div', 'article', 'li'])
                        if container:
                            # Find all text in container
                            all_text = container.get_text(separator=' | ', strip=True)
                            print(f"  Container Text: {all_text[:100]}...")
                            
                            # Look for headings
                            headings = container.find_all(['h1', 'h2', 'h3', 'h4'])
                            if headings:
                                for h in headings:
                                    h_text = h.get_text(strip=True)
                                    if h_text:
                                        print(f"  Heading: '{h_text}'")
                            
                            # Look for title attributes
                            title_attrs = container.find_all(attrs={'title': True})
                            for elem in title_attrs:
                                print(f"  Title Attr: '{elem.get('title', '')}'")
                    
                    # Save sample HTML
                    with open('cardmerchant_sample.html', 'w', encoding='utf-8') as f:
                        f.write(html[:15000])  # First 15k chars
                    print(f"\n📄 Saved HTML sample to cardmerchant_sample.html")
                    
                else:
                    print(f"❌ Status {response.status}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_cardmerchant())