import weaviate
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from config.config import Config
from model.chat_orchestrator import ChatOrchestratorRequest
from service import chat_orchestrator_service

router = APIRouter(
    prefix="/ragchat",
    tags=["ragchat"],
)

config = Config()
openai_client = OpenAI(api_key=config.OPEN_AI_KEY)

# --- PROTECTED INITIALIZATION ---
try:
    weaviate_client = weaviate.Client(
        url=config.WEAVIATE_BASE_URL,
        startup_period=2, # Reduced to fail faster and let the app boot
        timeout_config=(5, 60)
    )
    print("✅ Weaviate connected.")
except Exception as e:
    print(f"⚠️ Weaviate connection failed: {e}. App will still run.")
    weaviate_client = None
# --------------------------------

@router.post("/")
async def chat_with_customer(request: ChatOrchestratorRequest):
    # Safety check: if Weaviate failed to start, don't let the route crash
    if weaviate_client is None:
        raise HTTPException(
            status_code=503,
            detail="Chat service is temporarily unavailable (Database offline)."
        )

    ai_response = await chat_orchestrator_service.chat_with_customer(
        user_message=request.user_text,
        client=openai_client,
        weaviate_client=weaviate_client,
        user_id=request.user_id
    )
    return ai_response