from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class MonitoredProduct:
    """Model for monitored products"""
    id: Optional[int]
    sku: str
    store_name: str
    product_name: Optional[str] = None
    product_url: Optional[str] = None
    current_stock_status: str = 'Unknown'
    last_price: Optional[float] = None
    last_checked: Optional[datetime] = None
    added_date: Optional[datetime] = None
    is_active: bool = True

@dataclass
class StockHistory:
    """Model for stock history entries"""
    id: Optional[int]
    product_id: int
    stock_status: str
    price: Optional[float] = None
    checked_at: Optional[datetime] = None

@dataclass
class UserPreferences:
    """Model for user preferences"""
    user_id: str
    notification_enabled: bool = True
    preferred_stores: Optional[str] = None
    created_at: Optional[datetime] = None
