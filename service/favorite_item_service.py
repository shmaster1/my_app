from typing import List
from model.favorite_item_response import FavoriteItemResponse
from repository import favorite_item_repository


async def get_favorite_items_by_user_id(user_id: int) -> List[FavoriteItemResponse]:
    favorite_items = await favorite_item_repository.get_favorite_items(user_id)
    response_list =  [
        FavoriteItemResponse(
            item_id = favorite.item_id,
            item_name = favorite.item_name,
            price = favorite.price,
            stock_available = favorite.stock_available,
            image_url = favorite.image_url
        )
        for favorite in favorite_items
    ]
    return response_list

async def is_item_favorite(user_id: int, item_id: int) -> bool:
   return await favorite_item_repository.is_item_favorite(user_id, item_id)

async def add_item_to_favorites(user_id: int, item_id: int):
    await favorite_item_repository.add_item_to_favorite(user_id, item_id)

async def remove_item_from_favorites(user_id: int, item_id: int):
    await favorite_item_repository.remove_item_from_favorites(user_id, item_id)


