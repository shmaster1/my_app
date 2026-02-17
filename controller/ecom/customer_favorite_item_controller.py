from fastapi import APIRouter
from typing import List, Optional
from model.ecom.customer_favorite_item_request import CustomerFavoriteItemRequest
from model.ecom.customer_favorite_item_response import CustomerFavoriteItemResponse
from service.ecom import customer_favorite_item_service

router = APIRouter(
    prefix="/customer_favorite",
    tags=["customer_favorite"]
)



@router.get("/customer/{customer_id}")
async def get_favorite_items_by_customer_id(customer_id: int) -> List[CustomerFavoriteItemResponse]:
    return await customer_favorite_item_service.get_favorite_items_by_customer_id(customer_id)


@router.post("/")
async def create_favorite_item(favorite_item_request: CustomerFavoriteItemRequest) -> Optional[int]:
    return await customer_favorite_item_service.create_favorite_item(favorite_item_request)
