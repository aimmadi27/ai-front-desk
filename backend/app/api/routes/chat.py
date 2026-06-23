from fastapi import APIRouter
from pydantic import BaseModel
from app.services import gemini, session_store
from app.models.session import Message
from app.core.firestore import get_db
import uuid

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    business_id: str
    session_id: str | None = None
    message: str
    language: str = "en"


class ChatResponse(BaseModel):
    session_id: str
    reply: str


@router.post("/", response_model=ChatResponse)
async def web_chat(req: ChatRequest):
    session_id = req.session_id or f"web-{uuid.uuid4()}"

    session = session_store.get_session(session_id)
    if not session:
        session = session_store.create_session(
            call_sid=session_id,
            business_id=req.business_id,
            caller_number="web",
            language=req.language,
        )

    session_store.append_message(session_id, Message(role="user", content=req.message))
    session = session_store.get_session(session_id)

    db = get_db()
    biz_doc = db.collection("businesses").document(req.business_id).get()
    business = biz_doc.to_dict() if biz_doc.exists else {}

    reply = await gemini.get_ai_response(
        messages=session.messages,
        business=business,
        language=req.language,
    )
    session_store.append_message(session_id, Message(role="model", content=reply))

    return ChatResponse(session_id=session_id, reply=reply)
