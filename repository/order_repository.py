from datetime import date
from typing import Optional, List

from fastapi import HTTPException

from model import order_request
from model.item import Item
from model.order import Order
from model.order_item import OrderItem
from model.order_request import OrderRequest
from model.order_response import OrderResponse
from model.order_status import OrderStatus
from model.user_response import UserResponse
from repository.database import database

TABLE_ORDERS = "orders"
TABLE_ORDER_ITEMS = "order_items"
TABLE_ITEMS = "item"



async def get_by_id(order_id: int) -> Optional[Order]:
    # 1. Fetch order base data
    order_query = f"""
        SELECT *
        FROM {TABLE_ORDERS}
        WHERE id = :order_id
    """
    order_row = await database.fetch_one(order_query, values={"order_id": order_id})
    if not order_row:
        return None

    # 2. Fetch order items
    # Joined to get the item_name and current price from the Items table
    items_query = f"""
        SELECT it.id, it.item_name, it.price, ord.item_quantities
        FROM {TABLE_ORDER_ITEMS} ord
        JOIN {TABLE_ITEMS} it ON ord.item_id = it.id
        WHERE ord.order_id = :order_id
    """
    rows = await database.fetch_all(items_query, values={"order_id": order_id})

    # 3. Build OrderItem list and calculate total price
    order_items = []
    calculated_total_price = 0.0

    for row in rows:
        item_price = float(row["price"])
        item_qty = row["item_quantities"]

        # Mapping to the new OrderItem model
        order_items.append(
            OrderItem(
                item_id=row["id"],
                item_name=row["item_name"],
                price=item_price,
                quantity=item_qty
            )
        )
        # Summing up for the Order's total_price requirement
        calculated_total_price += item_price * item_qty

    # 4. Return the new Order model
    return Order(
        id=order_row["id"],
        user_id=order_row["user_id"],
        order_date=order_row["order_date"],
        shipping_address=order_row["shipping_address"],
        total_price=calculated_total_price,
        status=OrderStatus(order_row["status"]),  # Enforces TEMP or CLOSE
        order_items=order_items
    )

async def get_all_by_user_id(user_id: int) -> Optional[List[OrderResponse]]:

    # 1. Fetch all orders for the user
    # Logic: Order by status DESC so 'TEMP' (T) comes before 'CLOSE' (C)
    # to satisfy the "Pending order should always appear first" requirement.
    query = f"""
        SELECT *
        FROM {TABLE_ORDERS}
        WHERE user_id = :user_id
        ORDER BY CASE WHEN status = 'TEMP' THEN 0 ELSE 1 END, order_date DESC
    """
    order_rows = await database.fetch_all(query, values={"user_id": user_id})

    responses = []

    for row in order_rows:
        # 2. For each order, we must fetch its specific items to calculate totals
        # and satisfy the OrderResponse 'items' requirement.
        full_order_data = await get_by_id(row["id"])

        if full_order_data:
            # 3. Map the full Order model to the OrderResponse DTO
            responses.append(OrderResponse(
                order_id=full_order_data.id,
                order_date=full_order_data.order_date,
                shipping_address=full_order_data.shipping_address,
                total_price=full_order_data.total_price,
                status=full_order_data.status,
                items=full_order_data.order_items,
                # Helper logic for frontend styling and functionality
                is_modifiable=full_order_data.status == OrderStatus.TEMP,
                can_purchase=full_order_data.status == OrderStatus.TEMP and len(full_order_data.order_items) > 0
            ))

    return responses

async def get_temp_order_by_user(user_id: int):
    query = f"SELECT id FROM {TABLE_ORDERS} WHERE user_id = :user_id AND status = :status"
    values = {"user_id": user_id, "status": OrderStatus.TEMP.value}
    result = await database.fetch_one(query, values)
    if result:
        return result["id"]
    return None


async def get_temp_order_items(user_id: int):
    query = f"""
            SELECT oi.item_id FROM {TABLE_ORDER_ITEMS} oi
            JOIN {TABLE_ORDERS} o ON oi.order_id = o.id
            WHERE o.user_id = :user_id AND o.status = 'TEMP'
        """
    results = await database.fetch_all(query, values={"user_id": user_id})
    return [row["item_id"] for row in results]


async def get_temp_order_item_details(user_id: int = None):
    if user_id:
        query = f"""        
                SELECT * FROM {TABLE_ORDERS} o
                JOIN {TABLE_ORDER_ITEMS} oi ON o.id = oi.order_id
                JOIN {TABLE_ITEMS} it ON it.id = oi.item_id
                WHERE o.status = 'TEMP' AND o.user_id = :user_id
                """
        return await database.fetch_one(query, values={"user_id": user_id})

    query = f"""        
            SELECT * FROM {TABLE_ORDERS} o
            JOIN {TABLE_ORDER_ITEMS} oi ON o.id = oi.order_id
            JOIN {TABLE_ITEMS} it ON it.id = oi.item_id
            WHERE o.status = 'TEMP'
        """
    return await database.fetch_one(query)


async def create_order(order_request: OrderRequest, current_user: UserResponse) -> Optional[Order]:

    # Ensures "All or Nothing" to prevent orphan order(created in one table but not in the other)
    async with database.transaction():
        item_query = f"""
            SELECT price FROM {TABLE_ITEMS}
            WHERE id = :item_id
        """
        unit_price = await database.fetch_one(item_query, values= {"item_id": order_request.item_id})
        if not unit_price:
            raise HTTPException(status_code=404, detail="Item not found")  # ← repo layer
        item_unit_price = unit_price["price"]

        order_query = f"""
            INSERT INTO {TABLE_ORDERS} (user_id, order_date, shipping_address, total_price, status)
            VALUES (:user_id, :order_date, :shipping_address, :total_price, :status)
        """
        order_values = {
            "user_id": current_user.id,
            "order_date": date.today(),
            "shipping_address": order_request.shipping_address,
            "total_price": item_unit_price * order_request.quantity,
            "status": OrderStatus.TEMP.value
        }

        new_order_id = await database.execute(order_query, values=order_values)
        if not new_order_id:
            raise HTTPException(status_code=500, detail="Failed to create order")  # ← repo layer

        order_item_query = f"""
              INSERT INTO {TABLE_ORDER_ITEMS} (order_id, item_id, item_quantities)
              VALUES (:order_id, :item_id, :item_quantities)
           """
        order_item_values = {
            "order_id": new_order_id,
            "item_id": order_request.item_id,
            "item_quantities": order_request.quantity
        }

        await database.execute(order_item_query, values=order_item_values)

        created_order = await get_by_id(new_order_id)
        if not created_order:
            raise HTTPException(status_code=404, detail="Order not found")  # ← repo layer
        return created_order


async def add_new_item_to_temp_order(temp_order_id: int, order_request: OrderRequest) -> Optional[Order]:
    item_query = f"""
            SELECT price FROM {TABLE_ITEMS}
            WHERE id = :item_id
        """
    unit_price = await database.fetch_one(item_query, values={"item_id": order_request.item_id})
    item_unit_price = unit_price["price"]

    async with database.transaction():
        # 1. Insert the new item record
            item_query = f"""
                INSERT INTO {TABLE_ORDER_ITEMS} (order_id, item_id, item_quantities)
                VALUES (:order_id, :item_id, :item_quantities)
            """
            await database.execute(item_query, values={
                "order_id": temp_order_id,
                "item_id": order_request.item_id,
                "item_quantities": order_request.quantity
            })

        # 2. Update the total_price in the main TABLE_ORDERS
            update_query = f"""
                UPDATE {TABLE_ORDERS}
                SET total_price = total_price + :added_cost
                WHERE id = :order_id
            """
            await database.execute(update_query, values={
                "added_cost": item_unit_price * order_request.quantity,
                "order_id": temp_order_id
            })

            return await get_by_id(temp_order_id)


async def increase_item_quantity(temp_order_id: int, order_request: OrderRequest) ->Optional[Order]:
    item_query = f"""
               SELECT price FROM {TABLE_ITEMS}
               WHERE id = :item_id
           """
    unit_price = await database.fetch_one(item_query, values={"item_id": order_request.item_id})
    item_unit_price = unit_price["price"]

    async with database.transaction():
            # 1. update the quantity of the exist item record
            item_query = f"""
                UPDATE {TABLE_ORDER_ITEMS}
                SET item_quantities = item_quantities + :amount
                WHERE order_id = :order_id AND item_id = :item_id
            """
            await database.execute(item_query, values={
                "order_id": temp_order_id,
                "item_id": order_request.item_id,
                "amount": order_request.quantity
            })

        # 2. Update the total_price in the main 'orders' table (for the temp order id)
            update_query = f"""
                UPDATE {TABLE_ORDERS}
                SET total_price = total_price + :added_cost
                WHERE id = :order_id
            """
            await database.execute(update_query, values={
                "added_cost": item_unit_price * order_request.quantity,
                "order_id": temp_order_id
            })

    return await get_by_id(temp_order_id)


async def remove_item_from_order(item_id: int, user: UserResponse):
    order_query = f"SELECT * FROM {TABLE_ORDERS} WHERE user_id = :user_id AND status = 'TEMP'"
    order_row = await database.fetch_one(order_query, values={"user_id": user.id})

    if not order_row:
        return None

    temp_order = Order(**order_row)

    # 2. Fetch item data price and quantity in the order
    item_query = f"SELECT * FROM {TABLE_ITEMS} WHERE id = :id"
    item_row = await database.fetch_one(item_query, values={"id": item_id})
    item_result = Item(**item_row)

    quantity_query = f"""
        SELECT * FROM {TABLE_ORDER_ITEMS} 
        WHERE item_id = :item_id AND order_id = :order_id
    """
    quantity_row = await database.fetch_one(quantity_query, values={"item_id": item_id, "order_id": temp_order.id})

    if not item_row or not quantity_row:
        return None

    total_item_price = item_result.price * quantity_row["item_quantities"] # no specific model hence brackets and not dot annotation

    # 3. Delete the item from that specific order, update the total price, and remove from orders if it's the only item.
    async with database.transaction():
        delete_query = f"""
            DELETE FROM {TABLE_ORDER_ITEMS} 
            WHERE order_id = :order_id AND item_id = :item_id
        """
        await database.execute(delete_query, values={"order_id": temp_order.id, "item_id": item_id})

        update_query = f"""
            UPDATE {TABLE_ORDERS}
            SET total_price = total_price - :item_price
            WHERE id = :order_id
        """
        await database.execute(update_query, values={"item_price": total_item_price , "order_id": temp_order.id})

        order_query = f"SELECT * FROM {TABLE_ORDER_ITEMS} WHERE order_id = :order_id"
        order_rows = await database.fetch_all(order_query, values={"order_id": temp_order.id})
        if len(order_rows) == 0:
            delete_order_query = f"""
                       DELETE FROM {TABLE_ORDERS} 
                       WHERE id = :id
                   """
            await database.execute(delete_order_query, values={"id": temp_order.id})

        return "Deleted"


async def purchase_temp_order(user: UserResponse) -> Optional[OrderResponse]:
    temp_order_items_ids = await get_temp_order_items(user.id)
    temp_order = await get_temp_order_by_user(user.id)

    if not temp_order_items_ids or not temp_order:
        return None

    try:
        async with database.transaction():

            for item_id in temp_order_items_ids:
                quantity_query = f"""
                                    SELECT item_quantities FROM {TABLE_ORDER_ITEMS} 
                                    WHERE item_id = :item_id AND order_id = :order_id
                                """
                values = {"item_id": item_id , "order_id": temp_order}
                item_quantities = await database.fetch_val(quantity_query, values=values)

                if item_quantities is None: continue

                # Subtract stock with a "Positive Only" guard
                stock_query = f"""
                                UPDATE {TABLE_ITEMS}
                                SET stock_available = stock_available - :qty_to_remove
                                WHERE id = :id AND stock_available >= :qty_to_remove
                            """
                values = {"qty_to_remove": item_quantities, "id": item_id}
                updated_item_row = await database.execute(stock_query, values=values)

                # Check if the update actually happened (failed if updated_rows == 0)
                if updated_item_row == 0:
                    raise ValueError("Not enough in stock, please verify the current amount in stock.")

            status_query = f"""
                               UPDATE {TABLE_ORDERS}
                               SET status = :status
                               WHERE id = :id
                            """
            values = {"status": OrderStatus.CLOSED.value, "id": temp_order}
            await database.execute(status_query, values=values)

    except ValueError as e:
        # rollback already happened automatically
        raise HTTPException(status_code=409, detail=str(e))

    return await get_by_id(temp_order)






# async def get_order_items_by_order_id(order_id: int) -> List[OrderItem]:
#     items_query = f"""
#            SELECT it.id, it.item_name, it.price, ord.item_quantities
#            FROM {TABLE_ORDER_ITEMS} ord
#            JOIN {TABLE_ITEMS} it ON ord.item_id = it.id
#            WHERE ord.order_id = :order_id
#        """
#     result = await database.fetch_all(items_query, values={"order_id": order_id})
#
#




# # TODO 2. OLD ----> CHECK ALL SCENARIOS & PROBABLY WE CAN GET RID OF THE 3 FUNCTIONS: remove_item_from_order, add_exist_item_to_existing_order, add_new_item_to_existing_order
#
# async def edit_order_quantities(change: int, item_id: int, user: UserResponse) -> Optional[OrderResponse] | bool:
#     # 1. First, find the active order item details for this user
#     temp_item_details = await get_temp_order_item_details(user.id)
#     changed_quantity = int(temp_item_details["item_quantities"]) + change
#
#     if change > 0:
#
#         if change > temp_item_details["stock_available"]:
#             return None
#
#         async with database.transaction():
#             change_quantities_query = f"""
#                 UPDATE {TABLE_ORDER_ITEMS}
#                 SET item_quantities = :changed_quantity
#                 WHERE order_id = :order_id AND item_id = :item_id
#             """
#             values = {
#                 "item_id": item_id,
#                 "order_id": temp_item_details["order_id"],
#                 "changed_quantity": changed_quantity
#             }
#
#             await database.execute(change_quantities_query, values=values)
#
#             price_delta = temp_item_details["price"] * change
#
#             update_total_price_query = f"""
#                 UPDATE {TABLE_ORDERS}
#                 SET total_price = total_price + :changed_item_price
#                 WHERE id = :order_id
#             """
#             values = {"order_id": temp_item_details["order_id"], "changed_item_price": price_delta}
#
#             await database.execute(update_total_price_query, values=values)
#             return True
#
#     elif change < 0:
#
#         if changed_quantity < 0:
#             return None
#
#         async with database.transaction():
#             #1. change the quantity in order_item table
#             change_quantities_query = f"""
#                        UPDATE {TABLE_ORDER_ITEMS}
#                        SET item_quantities = item_quantities + :change
#                        WHERE order_id = :order_id AND item_id = :item_id
#                    """
#             values = {
#                 "item_id": item_id,
#                 "order_id": temp_item_details["order_id"],
#                 "change": change
#             }
#             await database.execute(change_quantities_query, values=values)
#
#             # 2. Check if the update changed quantities to 0
#             quantity_query = f"""
#                    SELECT item_quantities FROM {TABLE_ORDER_ITEMS}
#                    WHERE item_id = :item_id AND order_id = :order_id
#                """
#             values = {"item_id": item_id, "order_id": temp_item_details["order_id"]}
#
#             result = await database.fetch_val(quantity_query, values=values)
#
#             # 3. Remove first from order_items if there is item with 0
#             if result == 0:
#                 delete_order_items_query = f"""
#                     DELETE FROM {TABLE_ORDER_ITEMS}
#                     WHERE order_id = :order_id AND item_quantities = 0
#                 """
#                 await database.execute(delete_order_items_query, values={"order_id": temp_item_details["order_id"]})
#
#             # 4. Update total price after the change
#             price_delta = temp_item_details["price"] * change
#
#             update_total_price_query = f"""
#                        UPDATE {TABLE_ORDERS}
#                        SET total_price = total_price + :changed_item_price
#                        WHERE id = :order_id
#                    """
#             values = {"order_id": temp_item_details["order_id"], "changed_item_price": price_delta}
#
#             result = await database.execute(update_total_price_query, values=values)
#
#             # 5.Check if total price = 0 --> Remove order automatically
#             check_price_query = f"SELECT total_price FROM {TABLE_ORDERS} WHERE id = :order_id"
#             total_price = await database.fetch_val(check_price_query,
#                                                values={"order_id": temp_item_details["order_id"]})
#             if total_price < 0.01:
#
#             # 6. Delete the entire order from orders
#                 delete_orders_query = f"DELETE FROM {TABLE_ORDERS} WHERE user_id = :user_id AND status = 'TEMP'"
#                 await database.execute(delete_orders_query, values={"user_id": user.id})
#                 return False
#             return result
#
#     return None # will be re





