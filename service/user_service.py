from typing import List, Optional

from fastapi import HTTPException
from passlib.context import CryptContext
from starlette import status

from exceptions.exception import username_taken_exception
from model.user import User
from model.user_request import UserRequest
from model.user_response import UserResponse
from repository import user_repository

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


async def validate_unique_username(username: str) -> bool:
    existing_user = await user_repository.get_by_username(username)
    return existing_user is None


async def create_user(user_request: UserRequest) -> Optional[UserResponse]:
    if await validate_unique_username(user_request.username):
        hashed_password = get_password_hash(user_request.password)
        return await user_repository.create_user(user_request, hashed_password)
    else:
        print("Username already exists")
        raise username_taken_exception()


async def get_user_by_id(user_id: int) -> Optional[UserResponse]:
    user = await user_repository.get_by_id(user_id)
    if user:
        return UserResponse(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            country=user.country,
            city=user.city,
            is_registered=user.is_registered
        )
    else:
        return None


async def get_users() -> List[UserResponse]:
    users = await user_repository.get_users()
    return [UserResponse
            (id=user.id,
             username=user.username,
             first_name=user.first_name,
             last_name=user.last_name,
             email=user.email,
             phone = user.phone,
             country = user.country,
             city = user.city,
             is_registered = user.is_registered)
             for user in users]


async def get_user_by_username(username: str) -> User:
    return await user_repository.get_by_username(username)

async def is_username_taken(username: str) -> bool:
    return await user_repository.is_username_taken(username)

async def delete_user(user_id: int):
    is_deleted = await user_repository.delete_user(user_id)
    if is_deleted:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete user")

async def get_current_user_id(username: str) -> int:
    return await user_repository.get_current_user_id(username)