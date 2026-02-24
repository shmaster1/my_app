import weaviate
from fastapi import APIRouter
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
weaviate_client = weaviate.Client(url=config.WEAVIATE_BASE_URL, startup_period=5, timeout_config=(5, 60))


@router.post("/")
async def chat_with_customer(request: ChatOrchestratorRequest):
    ai_response = await chat_orchestrator_service.chat_with_customer(
        user_message=request.user_text,
        client=openai_client,
        weaviate_client=weaviate_client,
        user_id=request.user_id
    )
    return ai_response
