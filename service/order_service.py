from typing import Optional, List
from fastapi import HTTPException
from starlette import status
from model.order import Order
from model.order_request import OrderRequest
from model.order_response import OrderResponse
from model.user_response import UserResponse
from repository import order_repository


async def get_order_by_id(order_id: int) -> Optional[Order]:
    return await order_repository.get_by_id(order_id)


async def get_all_by_user_id(user_id: int) -> Optional[List[OrderResponse]]:
    return await order_repository.get_all_by_user_id(user_id)


async def add_item_to_order(order_request: OrderRequest, user: UserResponse) -> Optional[Order]:
    temp_order_id = await order_repository.get_temp_order_by_user(user.id)

    if not temp_order_id:
        return await order_repository.create_order(order_request, user)

    temp_order_items = await order_repository.get_temp_order_items(user.id)

    # order exist, item new
    if order_request.item_id not in temp_order_items:
        return await order_repository.add_new_item_to_temp_order(temp_order_id, order_request)

    # order exist, item exist
    else:
        return await order_repository.increase_item_quantity(temp_order_id, order_request)


async def remove_item(item_id: int, user: UserResponse):
    items_ids = await order_repository.get_temp_order_items(user.id)

    if not items_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User has no temp order")

    if len(items_ids) >= 1:
        if item_id not in items_ids:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not exist in temp order")
    return await order_repository.remove_item_from_order(item_id, user)


    # purchase temp order - only case that edit the stock!!!
async def purchase_order(user: UserResponse) -> Optional[OrderResponse]:
    closed_order = await order_repository.purchase_temp_order(user)
    if not closed_order:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to purchase order")
    return closed_order


##################################################################################################################
################################################## IMPORTRANT!!! ################################################
##################################################################################################################
# TODO: ADD VIEW CART TRIGGERED VIA UI WHEN USER NAVIGATES TO ORDER PAGE +
# TODO: THROW WARNING MSG FOR THE RELEVANT QUANTITIES OF ITEMS EXIST IIN HIS TEMP AFTER VALIDATING CURR STOCK!!!
