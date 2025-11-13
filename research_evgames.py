#!/usr/bin/env python3
"""Research script for EV Games store"""
import aiohttp
import asyncio
from bs4 import BeautifulSoup

async def research_ev_games():
    # Let's try some common NZ game store variations
    potential_urls = [
        'https://www.evgames.co.nz',
        'https://evgames.co.nz', 
        'https://www.ev-games.co.nz',
        'https://ev-games.co.nz',
        'https://evgames.nz',
        'https://www.evgames.nz'
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    async with aiohttp.ClientSession() as session:
        for url in potential_urls:
            try:
                print(f'Testing: {url}')
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        title = soup.find('title')
                        title_text = title.get_text() if title else 'No title'
                        
                        print(f'✅ FOUND: {url} - Status {response.status}')
                        print(f'   Title: {title_text}')
                        print(f'   Content length: {len(html)} chars')
                        
                        # Look for Pokemon-related content
                        if any(term in html.lower() for term in ['pokemon', 'tcg', 'trading card']):
                            print(f'   🎮 Pokemon content detected!')
                        
                        return url, html
                    else:
                        print(f'❌ {url} - Status {response.status}')
            except Exception as e:
                print(f'❌ {url} - Error: {str(e)[:50]}')
        
        print('\n⚠️ Could not find EV Games website')
        return None, None

if __name__ == "__main__":
    asyncio.run(research_ev_games())