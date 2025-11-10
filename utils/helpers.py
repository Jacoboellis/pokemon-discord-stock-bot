import re
import asyncio
from typing import Optional, Dict, Any
from urllib.parse import urlparse, urljoin

def clean_sku(sku: str) -> str:
    """Clean and normalize SKU format"""
    return re.sub(r'[^\w\-]', '', sku.upper())

def is_valid_url(url: str) -> bool:
    """Validate if a string is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def format_price(price: str) -> Optional[float]:
    """Extract and format price from string"""
    try:
        # Remove currency symbols and extract numbers
        price_clean = re.sub(r'[^\d.,]', '', price)
        price_clean = price_clean.replace(',', '')
        return float(price_clean)
    except (ValueError, AttributeError):
        return None

def create_embed_data(
    title: str, 
    description: str, 
    color: int = 0x3498db,
    fields: Optional[list] = None,
    thumbnail: Optional[str] = None
) -> Dict[str, Any]:
    """Create Discord embed data structure"""
    embed_data = {
        'title': title,
        'description': description,
        'color': color,
        'timestamp': None  # Will be set by Discord
    }
    
    if fields:
        embed_data['fields'] = fields
    
    if thumbnail:
        embed_data['thumbnail'] = {'url': thumbnail}
    
    return embed_data

async def rate_limited_request(delay: float = 1.0):
    """Decorator for rate limiting requests"""
    await asyncio.sleep(delay)

def extract_product_info(text: str) -> Dict[str, str]:
    """Extract product information from text"""
    info = {
        'name': '',
        'price': '',
        'availability': 'Unknown'
    }
    
    # Basic extraction patterns - can be enhanced per store
    price_pattern = r'\$?(\d+(?:\.\d{2})?)'
    price_match = re.search(price_pattern, text)
    if price_match:
        info['price'] = price_match.group(1)
    
    # Common availability indicators
    if any(word in text.lower() for word in ['in stock', 'available', 'add to cart']):
        info['availability'] = 'In Stock'
    elif any(word in text.lower() for word in ['out of stock', 'unavailable', 'sold out']):
        info['availability'] = 'Out of Stock'
    
    return info
