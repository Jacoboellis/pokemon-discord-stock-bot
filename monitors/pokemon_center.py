from typing import Dict, Any
from monitors.base_monitor import BaseMonitor

# Stock status constants
OUT_OF_STOCK_TEXT = ['Out of Stock', 'Sold Out', 'Currently Unavailable']

class PokemonCenterMonitor(BaseMonitor):
    """Monitor for Pokemon Center store"""
    
    def get_product_url(self, sku: str) -> str:
        """Generate Pokemon Center product URL"""
        # Pokemon Center URL structure may vary
        return f"https://www.pokemoncenter.com/product/{sku}"
    
    async def check_stock(self, sku: str, product_url: str = None) -> Dict[str, Any]:
        """Check stock for Pokemon Center product"""
        url = product_url or self.get_product_url(sku)
        
        result = {
            'sku': sku,
            'stock_status': 'Unknown',
            'price': None,
            'product_name': None,
            'product_url': url
        }
        
        try:
            html_content = await self.safe_request(url)
            if not html_content:
                return result
            
            soup = self.parse_html(html_content)
            
            # Look for product name
            name_element = soup.find('h1', class_='pdp-product-name')
            if name_element:
                result['product_name'] = name_element.get_text(strip=True)
            
            # Look for price
            price_element = soup.find('span', class_='sr-only') or soup.find('span', class_='price')
            if price_element:
                price_text = price_element.get_text(strip=True)
                result['price'] = self.extract_price(price_text)
            
            # Check stock status
            # Look for add to cart button or out of stock indicators
            add_to_cart = soup.find('button', class_='btn-primary') or soup.find('button', string='Add to Bag')
            out_of_stock = soup.find(text=OUT_OF_STOCK_TEXT)
            
            if add_to_cart and not add_to_cart.get('disabled'):
                result['stock_status'] = 'In Stock'
            elif out_of_stock:
                result['stock_status'] = 'Out of Stock'
            else:
                # Check for other stock indicators
                if 'add' in soup.get_text().lower() and 'cart' in soup.get_text().lower():
                    result['stock_status'] = 'In Stock'
                else:
                    result['stock_status'] = 'Out of Stock'
            
            self.logger.info(f"Pokemon Center {sku}: {result['stock_status']}")
            
        except Exception as e:
            self.logger.error(f"Error checking Pokemon Center stock for {sku}: {e}")
        
        return result
