from starlette import status
from fastapi import APIRouter

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get("/test", status_code=status.HTTP_200_OK)
def user_test():
    return "Hello from user test"





