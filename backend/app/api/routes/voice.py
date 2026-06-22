from fastapi import APIRouter, Form, Request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from app.services import session_store, gemini
from app.models.session import Message
from app.core.firestore import get_db

router = APIRouter(prefix="/voice", tags=["voice"])

BUSINESS_ID = "default"  # replaced per-business once multi-tenant is wired up


def _get_business(business_id: str) -> dict:
    db = get_db()
    doc = db.collection("businesses").document(business_id).get()
    if not doc.exists:
        return {"name": "this business", "services": [], "hours": {}}
    return doc.to_dict()


@router.post("/incoming")
async def incoming_call(
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
):
    session_store.create_session(
        call_sid=CallSid,
        business_id=BUSINESS_ID,
        caller_number=From,
    )

    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/voice/respond",
        method="POST",
        speech_timeout="auto",
        language="en-US",
    )
    gather.say(
        "Hello! Thank you for calling. How can I help you today?",
        voice="Polly.Joanna",
    )
    response.append(gather)
    return Response(content=str(response), media_type="application/xml")


@router.post("/respond")
async def handle_speech(
    CallSid: str = Form(...),
    SpeechResult: str = Form(default=""),
    From: str = Form(...),
):
    session = session_store.get_session(CallSid)
    if not session:
        response = VoiceResponse()
        response.say("Sorry, something went wrong. Please call back.")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    if not SpeechResult:
        response = VoiceResponse()
        gather = Gather(
            input="speech",
            action="/voice/respond",
            method="POST",
            speech_timeout="auto",
        )
        gather.say("I didn't catch that. Could you say that again?")
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")

    session_store.append_message(CallSid, Message(role="user", content=SpeechResult))
    session = session_store.get_session(CallSid)

    business = _get_business(session.business_id)
    ai_text = await gemini.get_ai_response(
        messages=session.messages,
        business=business,
        language=session.language,
    )

    session_store.append_message(CallSid, Message(role="model", content=ai_text))

    response = VoiceResponse()

    if "status=transfer" in ai_text.lower():
        response.say("Please hold while I connect you.")
        response.dial(business.get("owner_phone", ""))
        return Response(content=str(response), media_type="application/xml")

    gather = Gather(
        input="speech",
        action="/voice/respond",
        method="POST",
        speech_timeout="auto",
        language="es-US" if session.language == "es" else "en-US",
    )
    gather.say(ai_text)
    response.append(gather)
    return Response(content=str(response), media_type="application/xml")
