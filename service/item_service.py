from typing import List
from fastapi import HTTPException
from model.item import Item
from model.item_response import ItemResponse
from repository import item_repository


async def get_items() -> List[ItemResponse]:
    items = await item_repository.get_items()
    return [ItemResponse
            (id=item.id,
             item_name=item.item_name,
             price=item.price,
             stock_available=item.stock_available,
             image_url=item.image_url)
             for item in items]

async def filter_items(name: str) -> List[Item]:
    items = await item_repository.filter_items(name)
    return [Item
            (item_name=item.item_name,
             price=item.price,
             stock_available=item.stock_available)
            for item in items]

async def get_item_by_id(item_id: int) -> Item:
    item = await item_repository.get_item_by_id(item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


async def validate_item_exist_in_stock(item_id: int) -> Item:
    item = await get_item_by_id(item_id)

    if item.stock_available == 0:
        raise HTTPException(status_code=400, detail="Item is currently out of stock")
    return item

