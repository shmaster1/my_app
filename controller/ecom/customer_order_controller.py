from typing import Optional

from fastapi import APIRouter
from starlette import status

from model.ecom.customer_order import CustomerOrder
from model.ecom.customer_order_request import CustomerOrderRequest
from model.ecom.customer_order_response import CustomerOrderResponse
from service.ecom import customer_order_service

router = APIRouter(
    prefix="/customer_order",
    tags=["customer_order"]
)


@router.get("/{customer_order_id}", response_model=Optional[CustomerOrder])
async def get_customer_order_by_id(customer_order_id: int):
    return await customer_order_service.get_customer_order_by_id(customer_order_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_customer_order(customer_order_request: CustomerOrderRequest) -> CustomerOrderResponse:
    return await customer_order_service.create_customer_order(customer_order_request)


@router.put("/{customer_order_id}")
async def update_customer_order(customer_order_id: int, customer_order: CustomerOrder):
    await customer_order_service.update_customer_order(customer_order_id, customer_order)


@router.delete("/{customer_order_id}")
async def delete_customer_order(customer_order_id: int):
    await customer_order_service.delete_customer_order(customer_order_id)

