from typing import List

from pydantic import BaseModel

from model.ecom.customer import Customer
from model.ecom.customer_order import CustomerOrder


class CustomerOrderResponse(BaseModel):
    customer: Customer
    customer_orders: List[CustomerOrder]