from fastapi import HTTPException
from starlette import status


def token_exception():
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="The token provided is invalid."
    )
    return credential_exception


def username_taken_exception():
    username_taken_exception_response = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Provided username is already taken."
    )
    return username_taken_exception_response


def user_credentials_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password."
    )
    return token_exception_response

