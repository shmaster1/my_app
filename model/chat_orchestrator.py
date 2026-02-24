from pydantic import BaseModel

class ChatOrchestratorRequest(BaseModel):
    user_id: int
    user_text: str
