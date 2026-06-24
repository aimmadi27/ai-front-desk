from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Customer
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import uuid


class CustomerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create(self, business_id: str, phone: str, name: Optional[str] = None) -> Customer:
        result = await self.db.execute(
            select(Customer).where(Customer.business_id == business_id, Customer.phone == phone)
        )
        customer = result.scalar_one_or_none()
        if customer:
            return customer

        customer = Customer(
            id=str(uuid.uuid4()),
            business_id=business_id,
            phone=phone,
            name=name,
        )
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def update_after_booking(self, customer_id: str) -> None:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(select(Customer).where(Customer.id == customer_id))
        customer = result.scalar_one_or_none()
        if customer:
            await self.db.execute(
                update(Customer)
                .where(Customer.id == customer_id)
                .values(
                    last_appointment_at=now,
                    total_appointments=Customer.total_appointments + 1,
                )
            )
            await self.db.commit()

    async def get_lapsed(self, days: int = 30) -> List[Customer]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self.db.execute(
            select(Customer).where(
                Customer.last_appointment_at <= cutoff,
                Customer.reengaged == False,
            )
        )
        return list(result.scalars().all())

    async def mark_reengaged(self, customer_id: str) -> None:
        await self.db.execute(
            update(Customer).where(Customer.id == customer_id).values(reengaged=True)
        )
        await self.db.commit()
