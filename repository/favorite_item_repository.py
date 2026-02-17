from typing import List

from model.favorite_item_response import FavoriteItemResponse
from repository.database import database

TABLE_NAME_FAV = "favorite_items"
TABLE_NAME_ITEM = "item"


async def get_favorite_items(user_id: int) -> List[FavoriteItemResponse]:
    query = f"""
        SELECT 
            i.id AS item_id,
            i.item_name, 
            i.price, 
            i.stock_available,
            i.image_url
        FROM {TABLE_NAME_FAV} fav
        JOIN {TABLE_NAME_ITEM} i ON fav.item_id = i.id
        WHERE fav.user_id = :user_id
        """
    results = await database.fetch_all(query, values={"user_id": user_id})
    return [FavoriteItemResponse(**result) for result in results]


async def is_item_favorite(user_id: int, item_id: int) -> bool:
    query = """
    SELECT 1
    FROM favorite_items
    WHERE user_id = :user_id AND item_id = :item_id
    LIMIT 1
    """
    result = await database.fetch_one(
        query,
        values={"user_id": user_id, "item_id": item_id}
    )
    return result is not None


async def add_item_to_favorite(user_id: int, item_id: int):
    query = f"""
    INSERT INTO {TABLE_NAME_FAV} (user_id, item_id)
    VALUES (:user_id, :item_id)
    """
    values={"user_id": user_id, "item_id": item_id}

    await database.execute(query, values)

async def remove_item_from_favorites(user_id: int, item_id: int):
    query = f"""
        DELETE FROM {TABLE_NAME_FAV}
        WHERE user_id = :user_id
          AND item_id = :item_id
        """
    values = {"user_id": user_id, "item_id": item_id}

    await database.execute(query, values)
