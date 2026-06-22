from pydantic import BaseModel
from typing import List, Optional


class ServiceItem(BaseModel):
    name: str
    duration_minutes: int
    price_usd: float


class Business(BaseModel):
    id: str
    name: str
    phone_number: str
    owner_email: str
    services: List[ServiceItem] = []
    hours: dict = {}  # {"monday": "9am-6pm", ...}
    language: str = "en"  # en | es | both
    calendar_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    plan: str = "starter"  # starter | growth | pro
    active: bool = True
