from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings


def send_booking_email(
    to_email: str,
    customer_name: str,
    service: str,
    appointment_time: str,
    business_name: str,
) -> None:
    message = Mail(
        from_email="noreply@aifrontdesk.io",
        to_emails=to_email,
        subject=f"Appointment Confirmed — {business_name}",
        html_content=f"""
        <h2>Your appointment is confirmed!</h2>
        <p>Hi {customer_name},</p>
        <p>Your <strong>{service}</strong> appointment at <strong>{business_name}</strong>
        is confirmed for <strong>{appointment_time}</strong>.</p>
        <p>Reply to this email or call us if you need to reschedule.</p>
        <br>
        <p style="color:#888;font-size:12px">Powered by AI Front Desk</p>
        """,
    )
    sg = SendGridAPIClient(settings.sendgrid_api_key)
    sg.send(message)


def send_owner_alert(
    owner_email: str,
    business_name: str,
    event: str,
    details: str,
) -> None:
    message = Mail(
        from_email="noreply@aifrontdesk.io",
        to_emails=owner_email,
        subject=f"[AI Front Desk] {event} — {business_name}",
        html_content=f"<p>{details}</p>",
    )
    sg = SendGridAPIClient(settings.sendgrid_api_key)
    sg.send(message)
