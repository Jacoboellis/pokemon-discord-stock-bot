#!/usr/bin/env python3
"""Analyze Card Merchant JSON API"""
import asyncio
import aiohttp
import json

async def analyze_cardmerchant_json():
    url = "https://cardmerchant.co.nz/collections/pokemon-sealed.json"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    print("✅ Card Merchant JSON API working!")
                    print(f"JSON structure: {list(data.keys())}")
                    
                    collection = data.get('collection', {})
                    products = collection.get('products', [])
                    
                    print(f"Found {len(products)} products in JSON")
                    
                    # Analyze first few products
                    for i, product in enumerate(products[:3]):
                        print(f"\n=== Product {i+1} ===")
                        print(f"Title: {product.get('title', 'No title')}")
                        print(f"Handle: {product.get('handle', 'No handle')}")
                        print(f"ID: {product.get('id', 'No ID')}")
                        
                        variants = product.get('variants', [])
                        if variants:
                            variant = variants[0]  # First variant
                            price = variant.get('price', 0)
                            available = variant.get('available', False)
                            print(f"Price: ${float(price)/100:.2f} NZD")  # Shopify prices are in cents
                            print(f"Available: {available}")
                        
                        tags = product.get('tags', [])
                        print(f"Tags: {tags}")
                        
                        # Build product URL
                        handle = product.get('handle', '')
                        if handle:
                            product_url = f"https://cardmerchant.co.nz/collections/pokemon-sealed/products/{handle}"
                            print(f"URL: {product_url}")
                    
                    # Save JSON sample
                    with open('cardmerchant_api.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    print(f"\n📄 Saved full JSON to cardmerchant_api.json")
                    
                else:
                    print(f"❌ Status {response.status}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_cardmerchant_json())