from typing import Optional

from pydantic import BaseModel


class CustomerOrder(BaseModel):
    id: Optional[int]
    customer_id: Optional[int]
    item_name: str
    price: float