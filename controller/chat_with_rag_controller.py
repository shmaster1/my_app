import weaviate
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from weaviate.classes.init import Auth
from config.config import Config
from model.chat_orchestrator import ChatOrchestratorRequest
from service import chat_orchestrator_service

router = APIRouter(
    prefix="/ragchat",
    tags=["ragchat"],
)

config = Config()
openai_client = OpenAI(api_key=config.OPEN_AI_KEY)
groq_client = OpenAI(api_key=config.GROQ_API_KEY, base_url="https://api.groq.com/openai/v1") if config.GROQ_API_KEY else None
weaviate_client = None

def get_weaviate_client():
    global weaviate_client
    if weaviate_client is not None and weaviate_client.is_ready():
        return weaviate_client
    try:
        weaviate_client = weaviate.connect_to_weaviate_cloud(
            cluster_url=config.WEAVIATE_BASE_URL,
            auth_credentials=Auth.api_key(config.WEAVIATE_API_KEY),
            headers={"X-OpenAI-Api-Key": config.OPEN_AI_KEY}
        )
        print("✅ Connected to weaviate cloud.")
        return weaviate_client
    except:
        try:
            weaviate_client = weaviate.connect_to_local(skip_init_checks=True)  # TODO: remove skip_init_checks when running against cloud
            print("✅ Connected to weaviate locally")
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
        user_id=request.user_id,
        fallback_client=groq_client
    )
    return ai_response