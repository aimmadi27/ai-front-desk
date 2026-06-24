from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.repositories.business import BusinessRepository
from app.repositories.session import SessionRepository
from app.repositories.appointment import AppointmentRepository
from app.repositories.customer import CustomerRepository


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_business_repo(db: AsyncSession = None) -> BusinessRepository:
    return BusinessRepository(db)


async def get_session_repo(db: AsyncSession = None) -> SessionRepository:
    return SessionRepository(db)


async def get_appointment_repo(db: AsyncSession = None) -> AppointmentRepository:
    return AppointmentRepository(db)


async def get_customer_repo(db: AsyncSession = None) -> CustomerRepository:
    return CustomerRepository(db)
