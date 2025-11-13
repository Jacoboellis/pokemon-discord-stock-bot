#!/usr/bin/env python3
"""Check Card Merchant price format"""
import aiohttp
import asyncio
import json

async def check_prices():
    url = 'https://cardmerchant.co.nz/collections/pokemon-sealed/products.json'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                products = data.get('products', [])
                
                print('Card Merchant Price Analysis:')
                for i, product in enumerate(products[:3]):
                    print(f'\nProduct {i+1}: {product.get("title", "")}')
                    for variant in product.get('variants', []):
                        if variant.get('available'):
                            raw_price = variant.get('price')
                            print(f'  Raw price: {raw_price} ({type(raw_price)})')
                            if raw_price:
                                proper_price = float(raw_price) / 100.0
                                print(f'  Divided by 100: {proper_price}')
                                print(f'  Formatted: ${proper_price:.2f}')
                            break

if __name__ == "__main__":
    asyncio.run(check_prices())