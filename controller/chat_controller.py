from fastapi import APIRouter, Depends, HTTPException, Body
from openai import OpenAI
from config.config import Config
from model.chat_request import ChatRequest
from service import chat_service, user_service

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

config = Config()
openai_client = OpenAI(api_key=config.OPEN_AI_KEY)


@router.post("/")
async def chat_with_customer(request: ChatRequest):
    """
       Controller endpoint: receives user message and returns AI response.

       Strategy:
       - Sends message to chat_service
       - chat_service will ask GPT to extract intent
       - Routes to domain services (deterministic DB queries)
       - Returns structured response
       """

    # 1. Extract the user_id from the username currently logged in, on the first : so user can add : in his txt safely
    username = request.username
    user_text = request.user_text
    user_id = await user_service.get_current_user_id(username)

    try:
        ai_response = await chat_service.chat_with_customer(
            user_message=user_text,
            client=openai_client,
            user_id=user_id
        )
        return ai_response

    except HTTPException as e:
        # Let FastAPI handle status_code and detail
        raise e

    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(status_code=500, detail=str(e))
