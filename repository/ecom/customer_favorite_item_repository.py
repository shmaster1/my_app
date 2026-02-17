from typing import Optional, List

from model.ecom.customer_favorite_item import CustomerFavoriteItem
from repository.database import database

TABLE_NAME = "customer_favorite_item"


async def create_favorite_item(favorite_item: CustomerFavoriteItem) -> int:
    query = f"""
        INSERT INTO {TABLE_NAME} (customer_id, item_id)
        VALUES (:customer_id, :item_id)
    """
    values = {"customer_id": favorite_item.customer_id, "item_id": favorite_item.item_id}
    async with database.transaction():
        await database.execute(query, values)
        last_record_id = await database.fetch_one("SELECT LAST_INSERT_ID()")
    return last_record_id[0]


async def get_by_customer_id_and_item_id(customer_id: int, item_id: int) -> Optional[CustomerFavoriteItem]:
    query = f"SELECT * FROM {TABLE_NAME} WHERE customer_id=:customer_id AND item_id=:item_id"
    result = await database.fetch_one(query, values={"customer_id": customer_id, "item_id": item_id})

    if result:
        return CustomerFavoriteItem(**result)
    else:
        return None

async def get_favorite_items_by_customer_id(customer_id: int) -> List[CustomerFavoriteItem]:
    query = f"SELECT * FROM {TABLE_NAME} WHERE customer_id=:customer_id"
    results = await database.fetch_all(query, values={"customer_id": customer_id})
    return [CustomerFavoriteItem(**result) for result in results]
