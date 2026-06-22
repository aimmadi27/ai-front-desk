from pydantic import BaseModel
from typing import List


class Message(BaseModel):
    role: str  # "user" | "model"
    content: str


class Session(BaseModel):
    call_sid: str
    business_id: str
    caller_number: str
    messages: List[Message] = []
    language: str = "en"
    status: str = "active"  # active | completed | transferred
