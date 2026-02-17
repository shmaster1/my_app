from typing import Optional

from pydantic import BaseModel

from model.item_response import ItemResponse


class CustomerFavoriteItemResponse(BaseModel):
    id: Optional[int] = None
    customer_id: int
    item_response: ItemResponse



