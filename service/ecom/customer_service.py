from typing import Optional, List

from model.ecom.customer import Customer
from model.ecom.customer_status import CustomerStatus
from repository.ecom import customer_repository


async def get_customer_by_id(customer_id: int) -> Optional[Customer]:
    return await customer_repository.get_by_id(customer_id)


async def get_all_customers() -> List[Customer]:
    return await customer_repository.get_all()


async def create_customer(customer: Customer) -> int:
    if customer.status == CustomerStatus.VIP:
        vip_customers = await customer_repository.get_by_status(CustomerStatus.VIP)
        if len(vip_customers) < 4:
            return await customer_repository.create_customer(customer)
        else:
            raise Exception("Can't create new VIP customer - out of limit")
    else:
        return await customer_repository.create_customer(customer)

async def update_customer(customer_id: int, customer: Customer) -> Optional[Customer]:
    if customer.status == CustomerStatus.VIP: # מה רוצים שיהיה
        existing_customer = await customer_repository.get_by_id(customer.id) # מה הוא בפועל כרגע בד״ב
        if existing_customer.status is not CustomerStatus.VIP:
            vip_customers = await customer_repository.get_by_status(CustomerStatus.VIP) # כל אלה שהם ויאיפי כרגע בד״ב
            if len(vip_customers) < 4:
                return await customer_repository.update_customer(customer_id, customer)
            else:
                raise Exception("Can't create new VIP customer - out of limit")
    else:
        return await customer_repository.update_customer(customer_id, customer)
