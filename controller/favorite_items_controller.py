from typing import List
from fastapi import APIRouter, HTTPException
from starlette import status
from model.favorite_item_response import FavoriteItemResponse
from service import favorite_item_service, user_service, item_service

router = APIRouter(
    prefix="/favorites",
    tags=["favorites"]
)


@router.get("/user_id/{user_id}", response_model=List[FavoriteItemResponse])
async def get_favorite_items_by_user_id(user_id: int) -> List[FavoriteItemResponse]:
    favorite_items = await favorite_item_service.get_favorite_items_by_user_id(user_id)
    if not favorite_items:
        return []
    return favorite_items

@router.post("/user_id/{user_id}", status_code=status.HTTP_200_OK)
async def add_item_to_favorites(user_id: int, item_id: int):
    user = await user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    item = await item_service.get_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if await favorite_item_service.is_item_favorite(user_id, item_id):
        raise HTTPException(status_code=409, detail="Item already in favorites")

    await favorite_item_service.add_item_to_favorites(user_id, item_id)
    return {"message": "Item added to favorites"}

@router.delete("/user_id/{user_id}", status_code=status.HTTP_200_OK)
async def remove_item_from_favorites(user_id: int, item_id: int):
    user = await user_service.get_user_by_id(user_id)
    if user is not None:
        if await favorite_item_service.is_item_favorite(user_id, item_id):
            await favorite_item_service.remove_item_from_favorites(user_id, item_id)
            return {"message": "Item removed from favorites"}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item is not in favorites"
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User is not registered"
    )
