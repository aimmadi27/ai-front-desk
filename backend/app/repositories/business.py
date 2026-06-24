from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models import Business, Service, BusinessHour
from typing import Optional
import uuid


class BusinessRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, business_id: str) -> Optional[Business]:
        result = await self.db.execute(
            select(Business)
            .where(Business.id == business_id)
            .options(selectinload(Business.services), selectinload(Business.hours))
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> Optional[Business]:
        result = await self.db.execute(
            select(Business)
            .where(Business.phone_number == phone)
            .options(selectinload(Business.services), selectinload(Business.hours))
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Business:
        services_data = data.pop("services", [])
        hours_data = data.pop("hours", {})

        business = Business(id=str(uuid.uuid4()), **data)
        self.db.add(business)
        await self.db.flush()

        for svc in services_data:
            self.db.add(Service(id=str(uuid.uuid4()), business_id=business.id, **svc))

        for day, value in hours_data.items():
            if isinstance(value, str) and value.lower() == "closed":
                self.db.add(BusinessHour(id=str(uuid.uuid4()), business_id=business.id, day_of_week=day, is_closed=True))
            else:
                self.db.add(BusinessHour(id=str(uuid.uuid4()), business_id=business.id, day_of_week=day, is_closed=False))

        await self.db.commit()
        await self.db.refresh(business)
        return business

    async def update(self, business_id: str, data: dict) -> Optional[Business]:
        await self.db.execute(
            update(Business).where(Business.id == business_id).values(**data)
        )
        await self.db.commit()
        return await self.get(business_id)

    async def set_active(self, stripe_customer_id: str, active: bool) -> None:
        await self.db.execute(
            update(Business)
            .where(Business.stripe_customer_id == stripe_customer_id)
            .values(active=active)
        )
        await self.db.commit()
