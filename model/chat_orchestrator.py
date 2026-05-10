from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatOrchestratorRequest(BaseModel):
    user_id: int
    user_text: str
    history: Optional[List[ChatMessage]] = []
