from pydantic import BaseModel

from model.ecom.customer import Customer
from model.ecom.customer_order import CustomerOrder


class CustomerOrderRequest(BaseModel):
    customer: Customer
    customer_order: CustomerOrder