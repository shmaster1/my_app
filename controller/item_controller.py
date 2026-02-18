from typing import List, Optional
from fastapi import APIRouter, HTTPException
from starlette import status
from model.item import Item
from model.item_response import ItemResponse
from service import item_service

router = APIRouter(
    prefix="/item",
    tags=["item"],
)

# TODO: think if we want an explicit exception like in get users or just []

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[ItemResponse])
async def get_items():
    items = await item_service.get_items()
    if len(items) > 0:
        return items
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items found")


@router.get("/search", status_code=status.HTTP_200_OK, response_model=List[Item])
async def filter_items(name: str) -> List[Item]:
    items = await item_service.filter_items(name)
    if len(items) > 0:
        return items
    return []

@router.get("/{item_id}", status_code=status.HTTP_200_OK, response_model=ItemResponse)
async def get_item(item_id: int) -> Optional[Item]:
    item = await item_service.get_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item



