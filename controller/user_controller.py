from typing import List
from fastapi import APIRouter, Depends
from starlette import status
from exceptions.exception import token_exception, user_credentials_exception
from model.user_request import UserRequest
from model.user_response import UserResponse
from service import user_service, auth_service

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

# this endpoint isnt secured since we want to allow viewers (which obviously dont have token to pass in the req) to register
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(user_request: UserRequest):
    return await user_service.create_user(user_request)


# this endpoint is secured only valid token allows this call
@router.get("/", status_code=status.HTTP_200_OK, response_model=List[UserResponse])
async def get_users(user: UserResponse = Depends(auth_service.validate_user)):
    if user is None:
        raise token_exception()
    else:
        return await user_service.get_users() # this will happen only after we did all the checks e.g. validated token,
                                              # extracting the user id and checking it exists in db and he is active

@router.get("/check-username/{username}", status_code=status.HTTP_200_OK)
async def check_username(username: str):
    taken = await user_service.is_username_taken(username)
    return {"is_taken": taken}

@router.delete("/", status_code=status.HTTP_200_OK)
async def delete_user(user: UserResponse = Depends(auth_service.validate_user)):
    return await user_service.delete_user(user.id)

