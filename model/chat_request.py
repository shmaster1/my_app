from pydantic import BaseModel

class ChatRequest(BaseModel):
    username: str
    user_text: str
