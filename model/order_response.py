from datetime import date
from typing import List
from pydantic import BaseModel
from model.order_item import OrderItem
from model.order_status import OrderStatus

class OrderResponse(BaseModel):
    order_id: int
    order_date: date
    shipping_address: str
    total_price: float
    status: OrderStatus # Used to style 'TEMP' orders differently
    items: List[OrderItem]# List of items with title and price
    is_modifiable: bool# Helper: True if status is 'TEMP', false if 'CLOSE'
    can_purchase: bool# Helper: True if items > 0 and status is 'TEMP'
