"""
ARQ async job worker.
Run with: arq app.worker.WorkerSettings
"""
from arq import cron
from arq.connections import RedisSettings
from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.repositories.appointment import AppointmentRepository
from app.repositories.customer import CustomerRepository
from app.services.sms import send_reminder, send_sms

logger = get_logger(__name__)


async def send_appointment_reminders(ctx: dict) -> int:
    async with AsyncSessionLocal() as db:
        repo = AppointmentRepository(db)
        appointments = await repo.get_due_reminders()
        sent = 0

        for appt in appointments:
            if not appt.customer:
                continue

            from datetime import datetime, timezone, timedelta
            now = datetime.now(timezone.utc)
            delta = appt.start_at - now
            window = "24h" if delta > timedelta(hours=2) else "1h"

            if window == "24h" and appt.reminded_24h:
                continue
            if window == "1h" and appt.reminded_1h:
                continue

            send_reminder(
                to=appt.customer.phone,
                customer_name=appt.customer.name or "there",
                service=appt.service_name,
                appointment_time=appt.start_at.strftime("%I:%M %p on %A, %B %d"),
                business_name="",
                language=appt.customer.language or "en",
            )
            await repo.mark_reminded(appt.id, window)
            sent += 1

    logger.info("reminders_sent", count=sent)
    return sent


async def send_noshow_followups(ctx: dict) -> int:
    async with AsyncSessionLocal() as db:
        repo = AppointmentRepository(db)
        appointments = await repo.get_noshows()
        sent = 0

        for appt in appointments:
            if not appt.customer:
                continue

            lang = appt.customer.language or "en"
            body = (
                f"Hola {appt.customer.name or ''}, te echamos de menos hoy. "
                f"¿Te gustaría reprogramar tu cita de {appt.service_name}? Responde SÍ."
                if lang == "es" else
                f"Hi {appt.customer.name or 'there'}, we missed you today! "
                f"Would you like to reschedule your {appt.service_name}? Reply YES."
            )

            send_sms(to=appt.customer.phone, body=body)
            await repo.mark_no_show_followed_up(appt.id)
            sent += 1

    logger.info("noshow_followups_sent", count=sent)
    return sent


async def send_reengagement_messages(ctx: dict) -> int:
    async with AsyncSessionLocal() as db:
        repo = CustomerRepository(db)
        customers = await repo.get_lapsed(days=30)
        sent = 0

        for customer in customers:
            lang = customer.language or "en"
            biz_name = customer.business.name if hasattr(customer, "business") and customer.business else "us"
            body = (
                f"Hola {customer.name or ''}, ¡ha pasado un tiempo! "
                f"¿Listo para tu próxima cita en {biz_name}? Llámanos o responde aquí."
                if lang == "es" else
                f"Hi {customer.name or 'there'}, it's been a while! "
                f"Ready for your next visit at {biz_name}? Call us or reply here."
            )

            send_sms(to=customer.phone, body=body)
            await repo.mark_reengaged(customer.id)
            sent += 1

    logger.info("reengagement_sent", count=sent)
    return sent


async def startup(ctx: dict) -> None:
    logger.info("worker_starting")


async def shutdown(ctx: dict) -> None:
    logger.info("worker_stopping")


class WorkerSettings:
    functions = [send_appointment_reminders, send_noshow_followups, send_reengagement_messages]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    cron_jobs = [
        cron(send_appointment_reminders, minute={0, 30}),     # every 30 min
        cron(send_noshow_followups, hour={9, 14, 18}, minute=0),  # 3x daily
        cron(send_reengagement_messages, weekday=0, hour=10, minute=0),  # every Monday 10am
    ]
    max_jobs = 20
    job_timeout = 60
