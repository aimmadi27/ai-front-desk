from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timezone


class Message(BaseModel):
    role: str  # "user" | "model"
    content: str


class Session(BaseModel):
    call_sid: str
    business_id: str
    caller_number: str
    messages: List[Message] = []
    language: str = "en"
    status: str = "active"  # active | completed | transferred | missed
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
