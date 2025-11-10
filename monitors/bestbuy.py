from typing import Dict, Any
from monitors.base_monitor import BaseMonitor

class BestBuyMonitor(BaseMonitor):
    """Monitor for Best Buy store"""
    
    def get_product_url(self, sku: str) -> str:
        """Generate Best Buy product URL"""
        # Best Buy uses SKU in their URL structure
        return f"https://www.bestbuy.com/site/sku/{sku}.p"
    
    async def check_stock(self, sku: str, product_url: str = None) -> Dict[str, Any]:
        """Check stock for Best Buy product"""
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
            name_element = soup.find('h1', class_='sr-only') or soup.find('h1')
            if name_element:
                result['product_name'] = name_element.get_text(strip=True)
            
            # Look for price
            price_element = soup.find('span', class_='sr-only') or soup.find('[data-testid="customer-price"]')
            if price_element:
                price_text = price_element.get_text(strip=True)
                result['price'] = self.extract_price(price_text)
            
            # Check stock status
            # Best Buy specific selectors
            add_to_cart = soup.find('button', {'data-testid': 'add-to-cart-button'})
            sold_out = soup.find(text=['Sold Out', 'Currently Unavailable'])
            
            if add_to_cart and not add_to_cart.get('disabled'):
                result['stock_status'] = 'In Stock'
            elif sold_out:
                result['stock_status'] = 'Out of Stock'
            else:
                # Check page text for availability indicators
                page_text = soup.get_text().lower()
                if 'add to cart' in page_text:
                    result['stock_status'] = 'In Stock'
                elif any(phrase in page_text for phrase in ['sold out', 'unavailable', 'out of stock']):
                    result['stock_status'] = 'Out of Stock'
            
            self.logger.info(f"Best Buy {sku}: {result['stock_status']}")
            
        except Exception as e:
            self.logger.error(f"Error checking Best Buy stock for {sku}: {e}")
        
        return result
