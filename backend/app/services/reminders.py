from app.core.firestore import get_db
from app.services.sms import send_reminder, send_sms
from datetime import datetime, timezone, timedelta


def send_due_reminders() -> int:
    """Called by Cloud Scheduler every 30 minutes. Returns count sent."""
    db = get_db()
    now = datetime.now(timezone.utc)
    sent = 0

    appointments = db.collection("appointments").where("reminded", "==", False).stream()

    for doc in appointments:
        appt = doc.to_dict()
        appt_time = datetime.fromisoformat(appt["start_datetime"])
        delta = appt_time - now

        should_remind = timedelta(hours=23) < delta <= timedelta(hours=25) or \
                        timedelta(minutes=50) < delta <= timedelta(minutes=70)

        if not should_remind:
            continue

        send_reminder(
            to=appt["customer_phone"],
            customer_name=appt["customer_name"],
            service=appt["service"],
            appointment_time=appt_time.strftime("%I:%M %p on %A, %B %d"),
            business_name=appt["business_name"],
            language=appt.get("language", "en"),
        )
        doc.reference.update({"reminded": True})
        sent += 1

    return sent


def send_noshow_followups() -> int:
    """Called by Cloud Scheduler daily. Texts customers who missed their appointment."""
    db = get_db()
    now = datetime.now(timezone.utc)
    sent = 0

    appointments = (
        db.collection("appointments")
        .where("no_show_followed_up", "==", False)
        .stream()
    )

    for doc in appointments:
        appt = doc.to_dict()
        appt_time = datetime.fromisoformat(appt["start_datetime"])

        if now - appt_time < timedelta(hours=2):
            continue
        if now - appt_time > timedelta(hours=6):
            continue

        lang = appt.get("language", "en")
        if lang == "es":
            body = (
                f"Hola {appt['customer_name']}, te echamos de menos hoy. "
                f"¿Te gustaría reprogramar tu cita de {appt['service']}? "
                f"Responde SÍ y te ayudamos."
            )
        else:
            body = (
                f"Hi {appt['customer_name']}, we missed you today! "
                f"Would you like to reschedule your {appt['service']} appointment? "
                f"Reply YES and we'll get you booked."
            )

        send_sms(to=appt["customer_phone"], body=body)
        doc.reference.update({"no_show_followed_up": True})
        sent += 1

    return sent


def send_reengagement_messages() -> int:
    """Called by Cloud Scheduler weekly. Re-engages customers inactive for 30+ days."""
    db = get_db()
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=30)
    sent = 0

    customers = (
        db.collection("customers")
        .where("last_appointment", "<=", cutoff.isoformat())
        .where("reengaged", "==", False)
        .stream()
    )

    for doc in customers:
        customer = doc.to_dict()
        lang = customer.get("language", "en")

        if lang == "es":
            body = (
                f"Hola {customer['name']}, ¡ha pasado un tiempo! "
                f"¿Listo para tu próxima cita en {customer['business_name']}? "
                f"Llámanos o responde aquí."
            )
        else:
            body = (
                f"Hi {customer['name']}, it's been a while! "
                f"Ready for your next visit at {customer['business_name']}? "
                f"Give us a call or reply here to book."
            )

        send_sms(to=customer["phone"], body=body)
        doc.reference.update({"reengaged": True})
        sent += 1

    return sent
