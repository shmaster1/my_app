from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field
from model.order_item import OrderItem
from model.order_status import OrderStatus


class Order(BaseModel):
    id: int
    user_id: int
    order_date: date
    shipping_address: str
    total_price: float
    order_items: Optional[List[OrderItem]]
    status: OrderStatus
    # user_name: str = Field(alias="user")
