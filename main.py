from repository.database import database
from controller.auth_controller import router as auth_router
from controller.user_controller import router as user_router
from controller.item_controller import router as item_router
from controller.favorite_items_controller import router as favorite_item_router
from controller.order_controller import router as order_router
from controller.chat_controller import router as chat_router
from fastapi import FastAPI, Request
import json
import time
from starlette.responses import Response


app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(item_router)
app.include_router(favorite_item_router)
app.include_router(order_router)
app.include_router(chat_router)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# UNCOMMENT TO ALLOW VIEW OF XHRs IN TERMINAL

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     start = time.time()
#
#     # Read request body
#     body = await request.body()
#     try:
#         print("➡️ Request", request.method, request.url)
#         print("Payload:", json.dumps(json.loads(body.decode("utf-8")), indent=2))
#     except:
#         print("Payload:", body.decode("utf-8"))
#
#     # Call the actual endpoint
#     response = await call_next(request)
#
#     # Safely read the response body without breaking StreamingResponse
#     response_body = b""
#     async for chunk in response.body_iterator:
#         response_body += chunk
#
#     # Rebuild response safely
#     new_response = Response(
#         content=response_body,
#         status_code=response.status_code,
#         headers=dict(response.headers),
#         media_type=response.media_type
#     )
#
#     # Log response
#     try:
#         print("⬅️ Response:", json.dumps(json.loads(response_body.decode("utf-8")), indent=2))
#     except:
#         print("⬅️ Response:", response_body.decode("utf-8"))
#     print('-' * 80)
#     print()
#     print()
#     print(f"Duration: {time.time() - start:.2f}s")
#     return new_response
#
