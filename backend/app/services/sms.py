from twilio.rest import Client
from app.core.config import settings

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    return _client


def send_sms(to: str, body: str) -> str:
    client = get_client()
    message = client.messages.create(
        body=body,
        from_=settings.twilio_phone_number,
        to=to,
    )
    return message.sid


def send_booking_confirmation(
    to: str,
    customer_name: str,
    service: str,
    appointment_time: str,
    business_name: str,
    language: str = "en",
) -> str:
    if language == "es":
        body = (
            f"Hola {customer_name}, tu cita para {service} está confirmada "
            f"el {appointment_time} en {business_name}. "
            f"Responde CANCELAR para cancelar."
        )
    else:
        body = (
            f"Hi {customer_name}, your {service} appointment is confirmed "
            f"for {appointment_time} at {business_name}. "
            f"Reply CANCEL to cancel."
        )
    return send_sms(to, body)


def send_reminder(
    to: str,
    customer_name: str,
    service: str,
    appointment_time: str,
    business_name: str,
    language: str = "en",
) -> str:
    if language == "es":
        body = (
            f"Recordatorio: {customer_name}, tienes una cita para {service} "
            f"mañana a las {appointment_time} en {business_name}."
        )
    else:
        body = (
            f"Reminder: {customer_name}, you have a {service} appointment "
            f"tomorrow at {appointment_time} at {business_name}."
        )
    return send_sms(to, body)
