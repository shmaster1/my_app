from typing import Optional

from pydantic import BaseModel


class ItemResponse(BaseModel):
    id: int
    item_name: str
    price: float
    stock_available: int
    image_url: Optional[str] = None
