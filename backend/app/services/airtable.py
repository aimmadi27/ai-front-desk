import httpx
from app.core.config import settings


AIRTABLE_API_URL = "https://api.airtable.com/v0"


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.airtable_api_key}"}


async def upsert_customer(
    base_id: str,
    table_name: str,
    name: str,
    phone: str,
    service: str,
    business_name: str,
) -> None:
    url = f"{AIRTABLE_API_URL}/{base_id}/{table_name}"
    payload = {
        "fields": {
            "Name": name,
            "Phone": phone,
            "Last Service": service,
            "Business": business_name,
            "Source": "AI Front Desk",
        }
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload, headers=_headers())
