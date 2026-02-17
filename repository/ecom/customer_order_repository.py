from typing import Optional, List

from model.ecom.customer_order import CustomerOrder
from repository.database import database


async def get_by_id(customer_order_id: int) -> Optional[CustomerOrder]:
    query = "SELECT * FROM customer_order WHERE id=:customer_order_id"
    return await database.fetch_one(query, values={"customer_order_id": customer_order_id})


async def get_by_customer_id(customer_id: int) -> List[CustomerOrder]:
    query = "SELECT * FROM customer_order WHERE customer_id=:customer_id"
    return await database.fetch_all(query, values={"customer_id": customer_id})


async def create_customer_order(customer_order: CustomerOrder):
    query = """
       INSERT INTO customer_order (customer_id, item_name, price)
       VALUES (:customer_id, :item_name, :price)
    """

    values = {
        "customer_id": customer_order.customer_id,
        "item_name": customer_order.item_name,
        "price": customer_order.price,
    }
    await database.execute(query, values=values)


async def update_customer_order(customer_order_id: int, customer_order: CustomerOrder):
    query = """
        UPDATE customer_order
        SET customer_id=:customer_id,
        item_name=:item_name,
        price=:price,
        WHERE id=:customer_order_id
    """

    values = {
        "customer_order_id": customer_order_id,
        "customer_id": customer_order.customer_id,
        "item_name": customer_order.item_name,
        "price": customer_order.price,
    }

    await database.execute(query, values=values)


async def delete_customer_order(customer_order_id: int):
    query = "DELETE FROM customer_order WHERE id=:customer_order_id"

    await database.execute(query, values={"customer_order_id": customer_order_id})


