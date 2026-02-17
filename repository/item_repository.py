from typing import List

from model.item import Item
from model.item_response import ItemResponse
from repository.database import database

TABLE_NAME= "item"
TABLE_ORDER_ITEMS = "order_items"


async def get_items() -> List[ItemResponse]:
    query = f"SELECT * FROM {TABLE_NAME} WHERE stock_available > 0"
    results = await database.fetch_all(query)
    return [ItemResponse(**result) for result in results]

async def filter_items(name: str) -> List[Item]:
    words = [word.strip() for word in name.split(",") if word.strip()]
    if len(words) == 1:
        query = f"SELECT * FROM {TABLE_NAME} WHERE stock_available > 0 AND item_name LIKE :name"
        results = await database.fetch_all(query, values={"name": f"%{name}%"})
        return [Item(**result) for result in results]
    else:
        final_items = []
        for word in words:
            query = f"SELECT * FROM {TABLE_NAME} WHERE stock_available > 0 AND item_name LIKE :word"
            results = await database.fetch_all(query, values={"word": f"%{word}%"})
            for result in results:
                final_items.append(Item(**result))
        return final_items

async def get_item_by_id(item_id: int) -> Item | None:
    query = f"SELECT * FROM {TABLE_NAME} WHERE id=:item_id"
    result = await database.fetch_one(query, {"item_id": item_id})
    return result

async def get_item_by_name(name: str) -> Item | None:
    query = f"SELECT * FROM {TABLE_NAME} WHERE item_name=:item_name"
    result = await database.fetch_one(query, {"item_name": name})
    return result


