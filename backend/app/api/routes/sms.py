from fastapi import APIRouter, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from app.services import session_store, gemini, sms as sms_service
from app.models.session import Message, Session
import uuid

router = APIRouter(prefix="/sms", tags=["sms"])

BUSINESS_ID = "default"


@router.post("/incoming")
async def incoming_sms(
    MessageSid: str = Form(...),
    From: str = Form(...),
    Body: str = Form(...),
):
    session = session_store.get_session(From) or session_store.create_session(
        call_sid=From,
        business_id=BUSINESS_ID,
        caller_number=From,
    )

    session_store.append_message(From, Message(role="user", content=Body))
    session = session_store.get_session(From)

    from app.core.firestore import get_db
    db = get_db()
    business_doc = db.collection("businesses").document(BUSINESS_ID).get()
    business = business_doc.to_dict() if business_doc.exists else {}

    ai_text = await gemini.get_ai_response(
        messages=session.messages,
        business=business,
        language=session.language,
    )
    session_store.append_message(From, Message(role="model", content=ai_text))

    sms_service.send_sms(to=From, body=ai_text)

    response = MessagingResponse()
    return Response(content=str(response), media_type="application/xml")
