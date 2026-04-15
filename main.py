import weaviate
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from config.config import Config
from model.chat_orchestrator import ChatOrchestratorRequest
from service import chat_orchestrator_service

router = APIRouter(prefix="/ragchat", tags=["ragchat"])
config = Config()
openai_client = OpenAI(api_key=config.OPEN_AI_KEY)
weaviate_client = None  # not initialized at import time

def get_weaviate_client():
    global weaviate_client
    if weaviate_client is not None:
        return weaviate_client
    try:
        weaviate_client = weaviate.Client(
            url=config.WEAVIATE_BASE_URL,
            startup_period=2,
            timeout_config=(5, 15)  # tighter timeout
        )
        print("✅ Weaviate connected.")
        return weaviate_client
    except Exception as e:
        print(f"⚠️ Weaviate connection failed: {e}")
        return None

@router.post("/")
async def chat_with_customer(request: ChatOrchestratorRequest):
    client = get_weaviate_client()
    if client is None:
        raise HTTPException(
            status_code=503,
            detail="Chat service is temporarily unavailable."
        )
    ai_response = await chat_orchestrator_service.chat_with_customer(
        user_message=request.user_text,
        client=openai_client,
        weaviate_client=client,
        user_id=request.user_id
    )
    return ai_response