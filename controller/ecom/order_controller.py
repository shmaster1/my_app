
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from starlette import status

from model.ecom.order import Order

router = APIRouter(
    prefix="/order",
    tags=["order"]
)

orders = {}

@router.get("/order_id/{order_id}", response_model=Order)
def get_order_by_id(order_id: int):
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(order: Order):
    if order.order_id in orders:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order ID already exists")
    orders[order.order_id] = order
    return order

@router.put("/{order_id}", response_model=Order)
def update_order(order_id: int, order: Order):
    existing_order = orders.get(order_id)
    if not existing_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    else:
        orders[order_id] = order
    return order

@router.delete("/{order_id}")
def delete_order(order_id: int):
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    del orders[order_id]


@router.get("/customer", response_model=List[Order])
def get_order_by_customer(customer_name: Optional[str] = Query(None)) -> List[Order]:
    order_results = []
    for order in orders.values():
        if order.customer_name == customer_name:
            order_results.append(order)

    return order_results



