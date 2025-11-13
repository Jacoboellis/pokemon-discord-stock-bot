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
        """Create aiohttp session with proper headers and connection pooling"""
        if not self.session:
            # Enhanced connection pooling settings
            connector = aiohttp.TCPConnector(
                limit=20,           # Total connection limit
                limit_per_host=10,  # Connections per host
                ttl_dns_cache=300,  # DNS cache TTL (5 minutes)
                use_dns_cache=True,
                keepalive_timeout=60,  # Keep connections alive for 1 minute
                enable_cleanup_closed=True
            )
            
            # Timeout configuration
            timeout = aiohttp.ClientTimeout(
                total=self.config.request_timeout if hasattr(self.config, 'request_timeout') else 30,
                connect=10,  # Connection timeout
                sock_read=10  # Socket read timeout
            )
            
            # Common browser headers for better compatibility
            headers = {
                'User-Agent': self.config.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,en-NZ;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Charset': 'utf-8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=headers,
                raise_for_status=False,  # Handle status codes manually
                cookie_jar=aiohttp.CookieJar(unsafe=True)  # Allow cookies
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
    
    async def safe_request(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Make a safe HTTP request with retry logic and error handling"""
        self.create_session_if_needed()
        
        for attempt in range(max_retries + 1):
            try:
                # Add exponential backoff delay for retries
                if attempt > 0:
                    delay = 2 ** attempt  # 2, 4, 8 seconds
                    self.logger.info(f"Retrying {url} in {delay} seconds (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        return content
                    elif response.status == 429:  # Rate limited
                        retry_after = int(response.headers.get('Retry-After', 60))
                        self.logger.warning(f"Rate limited for {url}, waiting {retry_after} seconds")
                        await asyncio.sleep(retry_after)
                        continue
                    elif response.status in (502, 503, 504):  # Server errors - retry
                        self.logger.warning(f"Server error {response.status} for {url}, retrying...")
                        continue
                    else:
                        self.logger.warning(f"HTTP {response.status} for {url}")
                        return None
                        
            except asyncio.TimeoutError:
                self.logger.error(f"Timeout requesting {url} (attempt {attempt + 1})")
                if attempt == max_retries:
                    return None
            except aiohttp.ClientError as e:
                self.logger.error(f"Client error requesting {url}: {e} (attempt {attempt + 1})")
                if attempt == max_retries:
                    return None
            except Exception as e:
                self.logger.error(f"Unexpected error requesting {url}: {e} (attempt {attempt + 1})")
                if attempt == max_retries:
                    return None
        
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
