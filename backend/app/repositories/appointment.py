from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models import Appointment, Customer
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import uuid


class AppointmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Appointment:
        appt = Appointment(id=str(uuid.uuid4()), **data)
        self.db.add(appt)
        await self.db.commit()
        await self.db.refresh(appt)
        return appt

    async def get(self, appointment_id: str) -> Optional[Appointment]:
        result = await self.db.execute(
            select(Appointment)
            .where(Appointment.id == appointment_id)
            .options(selectinload(Appointment.customer), selectinload(Appointment.service))
        )
        return result.scalar_one_or_none()

    async def list_by_business(self, business_id: str, status: Optional[str] = None) -> List[Appointment]:
        q = select(Appointment).where(Appointment.business_id == business_id)
        if status:
            q = q.where(Appointment.status == status)
        q = q.order_by(Appointment.start_at.desc())
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def get_due_reminders(self) -> List[Appointment]:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(Appointment)
            .where(
                Appointment.status == "confirmed",
                Appointment.start_at.between(now + timedelta(hours=23), now + timedelta(hours=25))
                | Appointment.start_at.between(now + timedelta(minutes=50), now + timedelta(minutes=70)),
                (Appointment.reminded_24h == False) | (Appointment.reminded_1h == False),
            )
            .options(selectinload(Appointment.customer))
        )
        return list(result.scalars().all())

    async def get_noshows(self) -> List[Appointment]:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(Appointment)
            .where(
                Appointment.status == "confirmed",
                Appointment.start_at.between(now - timedelta(hours=6), now - timedelta(hours=2)),
                Appointment.no_show_followed_up == False,
            )
            .options(selectinload(Appointment.customer))
        )
        return list(result.scalars().all())

    async def mark_reminded(self, appointment_id: str, window: str) -> None:
        field = "reminded_24h" if window == "24h" else "reminded_1h"
        await self.db.execute(
            update(Appointment).where(Appointment.id == appointment_id).values(**{field: True})
        )
        await self.db.commit()

    async def mark_no_show_followed_up(self, appointment_id: str) -> None:
        await self.db.execute(
            update(Appointment).where(Appointment.id == appointment_id).values(no_show_followed_up=True)
        )
        await self.db.commit()

    async def update_status(self, appointment_id: str, status: str) -> None:
        await self.db.execute(
            update(Appointment).where(Appointment.id == appointment_id).values(status=status)
        )
        await self.db.commit()
