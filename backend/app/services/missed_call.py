from app.services.sms import send_sms
from app.core.firestore import get_db


def handle_missed_call(business_id: str, caller_number: str) -> None:
    """Texts back a caller who called outside business hours."""
    db = get_db()
    doc = db.collection("businesses").document(business_id).get()
    if not doc.exists:
        return

    business = doc.to_dict()
    lang = business.get("language", "en")
    name = business.get("name", "us")

    if lang == "es":
        body = (
            f"Hola, llamaste a {name} pero estamos cerrados ahora. "
            f"¡Responde aquí y nuestro asistente de IA te ayudará a programar una cita!"
        )
    else:
        body = (
            f"Hi! You just called {name} but we're currently closed. "
            f"Reply to this message and our AI assistant will help you book an appointment right now!"
        )

    send_sms(to=caller_number, body=body)

    db.collection("missed_calls").add({
        "business_id": business_id,
        "caller_number": caller_number,
        "recovered": False,
    })
