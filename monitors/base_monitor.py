import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from bs4 import BeautifulSoup

from utils.config import Config

class BaseMonitor(ABC):
    """Base class for store monitors"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = None
    
    def create_session_if_needed(self):
        """Create aiohttp session with proper headers if it doesn't exist"""
        if not self.session:
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            timeout = aiohttp.ClientTimeout(total=30)
            
            headers = {
                'User-Agent': self.config.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=headers
            )
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    @abstractmethod
    async def check_stock(self, sku: str, product_url: str = None) -> Dict[str, Any]:
        """Check stock for a specific SKU
        
        Returns:
            dict: {
                'sku': str,
                'stock_status': str,  # 'In Stock', 'Out of Stock', 'Unknown'
                'price': float or None,
                'product_name': str or None,
                'product_url': str or None
            }
        """
        pass
    
    @abstractmethod
    def get_product_url(self, sku: str) -> str:
        """Generate product URL for SKU"""
        pass
    
    async def safe_request(self, url: str) -> Optional[str]:
        """Make a safe HTTP request with error handling"""
        try:
            self.create_session_if_needed()
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    return content
                else:
                    self.logger.warning(f"HTTP {response.status} for {url}")
                    return None
                    
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout requesting {url}")
            return None
        except Exception as e:
            self.logger.error(f"Error requesting {url}: {e}")
            return None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup"""
        return BeautifulSoup(html_content, 'html.parser')
    
    def extract_price(self, price_text: str) -> Optional[float]:
        """Extract price from text"""
        try:
            import re
            # Remove currency symbols and extract numbers
            price_clean = re.sub(r'[^\d.,]', '', price_text)
            price_clean = price_clean.replace(',', '')
            return float(price_clean)
        except (ValueError, AttributeError):
            return None
