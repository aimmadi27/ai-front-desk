from fastapi import APIRouter, Form, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from app.services import session_store, gemini
from app.services.missed_call import handle_missed_call
from app.models.session import Message
from app.core.firestore import get_db
from datetime import datetime, timezone

router = APIRouter(prefix="/voice", tags=["voice"])

BUSINESS_ID = "default"


def _get_business(business_id: str) -> dict:
    db = get_db()
    doc = db.collection("businesses").document(business_id).get()
    if not doc.exists:
        return {"name": "this business", "services": [], "hours": {}}
    return doc.to_dict()


def _is_business_open(business: dict) -> bool:
    now = datetime.now(timezone.utc)
    day = now.strftime("%A").lower()
    hours = business.get("hours", {})
    return day in hours and hours[day].lower() != "closed"


def _detect_language(speech: str) -> str:
    spanish_words = {"hola", "buenos", "necesito", "quiero", "cita", "gracias", "ayuda"}
    words = set(speech.lower().split())
    return "es" if words & spanish_words else "en"


@router.post("/incoming")
async def incoming_call(
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
):
    business = _get_business(BUSINESS_ID)

    if not _is_business_open(business):
        handle_missed_call(BUSINESS_ID, From)
        response = VoiceResponse()
        response.say(
            "Thank you for calling! We're currently closed but we just texted you "
            "so our AI assistant can help you book an appointment right now.",
            voice="Polly.Joanna",
        )
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

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
        f"Hello! Thank you for calling {business.get('name', 'us')}. "
        "How can I help you today?",
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

    detected_lang = _detect_language(SpeechResult)
    if detected_lang != session.language:
        session_store.get_db if False else None
        db = get_db()
        db.collection("sessions").document(CallSid).update({"language": detected_lang})
        session.language = detected_lang

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

    lang_code = "es-US" if session.language == "es" else "en-US"
    gather = Gather(
        input="speech",
        action="/voice/respond",
        method="POST",
        speech_timeout="auto",
        language=lang_code,
    )
    gather.say(ai_text)
    response.append(gather)
    return Response(content=str(response), media_type="application/xml")


@router.post("/status")
async def call_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
):
    if CallStatus in ("completed", "no-answer", "busy", "failed"):
        db = get_db()
        status = "completed" if CallStatus == "completed" else "missed"
        db.collection("sessions").document(CallSid).update({"status": status})
    return Response(content="", status_code=204)
