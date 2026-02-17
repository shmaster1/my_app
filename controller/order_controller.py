from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from model.order import Order
from model.order_request import OrderRequest
from model.order_response import OrderResponse
from model.user_response import UserResponse
from service import order_service, auth_service

router = APIRouter(
    prefix="/order",
    tags=["order"]
)


@router.get("/order_id/{order_id}", status_code=status.HTTP_200_OK, response_model=Optional[Order])
async def get_order_by_id(order_id: int):
    order = await order_service.get_order_by_id(order_id)
    if order:
        return order
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")


@router.get("/user_id/{user_id}", status_code=status.HTTP_200_OK, response_model=Optional[List[OrderResponse]])
async def get_order_by_user_id(user_id: int):
    orders = await order_service.get_all_by_user_id(user_id)
    if orders:
        return orders
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No orders found for this user")


@router.post("/item", status_code=status.HTTP_201_CREATED)
async def add_item_to_order(order_request: OrderRequest, user: UserResponse = Depends(auth_service.validate_user)):
    return await order_service.add_item_to_order(order_request, user)


@router.delete("/item/{item_id}", status_code=status.HTTP_200_OK)
async def delete_item_from_order(item_id: int, user: UserResponse = Depends(auth_service.validate_user)):
    return await order_service.remove_item(item_id, user)


@router.post("/purchase_order", status_code=status.HTTP_201_CREATED, response_model=Optional[Order])
async def purchase_order(user: UserResponse = Depends(auth_service.validate_user)):
    return await order_service.purchase_order(user)

