from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models import Session, Message
from datetime import datetime, timezone
from typing import Optional, List
import uuid


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, session_id: str) -> Optional[Session]:
        result = await self.db.execute(
            select(Session)
            .where(Session.id == session_id)
            .options(selectinload(Session.messages))
        )
        return result.scalar_one_or_none()

    async def list_by_business(self, business_id: str, limit: int = 100) -> List[Session]:
        result = await self.db.execute(
            select(Session)
            .where(Session.business_id == business_id)
            .options(selectinload(Session.messages))
            .order_by(Session.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(
        self,
        session_id: str,
        business_id: str,
        caller_number: str,
        channel: str = "voice",
        language: str = "en",
    ) -> Session:
        session = Session(
            id=session_id,
            business_id=business_id,
            caller_number=caller_number,
            channel=channel,
            language=language,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def append_message(self, session_id: str, role: str, content: str) -> Message:
        message = Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
        )
        self.db.add(message)
        await self.db.commit()
        return message

    async def update_status(self, session_id: str, status: str) -> None:
        values: dict = {"status": status}
        if status in ("completed", "transferred", "missed"):
            values["ended_at"] = datetime.now(timezone.utc)
        await self.db.execute(
            update(Session).where(Session.id == session_id).values(**values)
        )
        await self.db.commit()

    async def update_language(self, session_id: str, language: str) -> None:
        await self.db.execute(
            update(Session).where(Session.id == session_id).values(language=language)
        )
        await self.db.commit()

    async def link_appointment(self, session_id: str, appointment_id: str) -> None:
        await self.db.execute(
            update(Session).where(Session.id == session_id).values(appointment_id=appointment_id)
        )
        await self.db.commit()
