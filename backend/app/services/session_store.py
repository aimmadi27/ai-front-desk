from app.core.firestore import get_db
from app.models.session import Session, Message
from typing import Optional


COLLECTION = "sessions"


def get_session(call_sid: str) -> Optional[Session]:
    db = get_db()
    doc = db.collection(COLLECTION).document(call_sid).get()
    if doc.exists:
        return Session(**doc.to_dict())
    return None


def save_session(session: Session) -> None:
    db = get_db()
    db.collection(COLLECTION).document(session.call_sid).set(session.model_dump())


def append_message(call_sid: str, message: Message) -> Session:
    session = get_session(call_sid)
    if not session:
        raise ValueError(f"Session {call_sid} not found")
    session.messages.append(message)
    save_session(session)
    return session


def create_session(
    call_sid: str,
    business_id: str,
    caller_number: str,
    language: str = "en",
) -> Session:
    session = Session(
        call_sid=call_sid,
        business_id=business_id,
        caller_number=caller_number,
        language=language,
    )
    save_session(session)
    return session
