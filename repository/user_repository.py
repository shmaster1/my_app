from typing import Optional, List

from model.user import User
from model.user_request import UserRequest
from model.user_response import UserResponse
from repository.database import database
from service import user_service

USERS_TABLE = "users"
TABLE_FAVORITES = "favorite_items"
TABLE_ORDERS = "orders"
TABLE_ORDER_ITEMS = "order_items"

async def get_by_username(username: str) -> Optional[User]:
    query = f"SELECT * FROM {USERS_TABLE} WHERE username=:username AND is_registered=:is_registered"
    result = await database.fetch_one(query, values={"username": username, "is_registered": True})
    if result:
        return User(**result)
    else:
        return None

async def get_by_id(user_id: int) -> Optional[User]:
    query = f"SELECT * FROM {USERS_TABLE} WHERE id=:user_id AND is_registered=:is_registered"
    result = await database.fetch_one(query, values={"user_id": user_id, "is_registered": True})
    if result:
        return User(**result)
    else:
        return None

async def get_users() -> List[User]:
    query = f"SELECT * FROM {USERS_TABLE} WHERE is_registered=:is_registered"
    results = await database.fetch_all(query, values={"is_registered": True})
    return [User(**result) for result in results]


async def create_user(user: UserRequest, hashed_password: str) -> Optional[UserResponse]:
    query = f"""
        INSERT INTO {USERS_TABLE} (username, first_name, last_name, email, phone, country, city, hashed_password, is_registered)
        VALUES (:username, :first_name, :last_name, :email, :phone, :country, :city, :hashed_password, :is_registered)
    """
    user_dict = user.dict()
    del user_dict["password"]
    values = {**user_dict, "hashed_password": hashed_password, "is_registered": True}

    await database.execute(query, values)

    select_query = f"SELECT * FROM {USERS_TABLE} WHERE username = :username"
    result = await database.fetch_one(select_query, {"username": user.username})

    if result:
        return UserResponse(**result)
    return None


async def is_username_taken(username: str) -> bool:
    # We only need to select '1' (or the ID) to be efficient, no need for the whole data '*'
    query = f"SELECT 1 FROM {USERS_TABLE} WHERE username = :username"
    result = await database.fetch_one(query, values={"username": username})
    return result is not None

async def delete_user(user_id: int):
    delete_items_query = f"""
        DELETE oi FROM {TABLE_ORDER_ITEMS} oi
        JOIN {TABLE_ORDERS} o ON oi.order_id = o.id
        WHERE o.user_id = :user_id
    """
    await database.execute(delete_items_query, values={"user_id": user_id})

    delete_orders_query = f"DELETE FROM {TABLE_ORDERS} WHERE user_id = :user_id"
    await database.execute(delete_orders_query, values={"user_id": user_id})

    delete_favorites_query = f"DELETE FROM {TABLE_FAVORITES} WHERE user_id = :user_id"
    await database.execute(delete_favorites_query, values={"user_id": user_id})

    delete_user_query = f"DELETE FROM {USERS_TABLE} WHERE id = :user_id"
    await database.execute(delete_user_query, values={"user_id": user_id})

    return True

async def get_current_user_id(username: str) -> int:
    query = f"SELECT id FROM {USERS_TABLE} WHERE username = :username"
    result = await database.fetch_one(query, values={"username": username})
    return result[0] # returns as tuple e.g. (1,)
