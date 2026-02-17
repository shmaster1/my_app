from typing import Optional, List

from fastapi import APIRouter, HTTPException
from starlette import status

from model.ecom.customer import Customer
from service.ecom import customer_service

router = APIRouter(
    prefix="/customer",
    tags=["customer"]
)


@router.get("/customer_id/{customer_id}", response_model=Customer)
async def get_customer_by_id(customer_id: int) -> Optional[Customer]:
    customer = await customer_service.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer with customer_id {customer_id} not found")
    return customer


@router.get("/all")
async def get_all_customers() -> List[Customer]:
    return await customer_service.get_all_customers()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_customer(customer: Customer):
    try:
        await customer_service.create_customer(customer)
    except Exception:
        raise HTTPException(status_code=400, detail="Can't create new VIP customer - out of limit")

@router.put("/{customer_id}", status_code=status.HTTP_200_OK)
async def update_customer(customer_id: int, customer: Customer):
    try:
        return await customer_service.update_customer(customer_id, customer)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Can't update customer - out of limit"
        )




