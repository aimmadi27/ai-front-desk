import google.generativeai as genai
from app.core.config import settings
from app.models.session import Message
from typing import List

genai.configure(api_key=settings.gemini_api_key)

_model = genai.GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT = """You are an AI front desk agent for {business_name}, a {business_type} in Charlotte, NC.
Your job is to help customers:
1. Book, reschedule, or cancel appointments
2. Answer questions about services, hours, and pricing
3. Take messages for the owner

Business hours: {hours}
Services offered: {services}

Rules:
- Be warm, professional, and concise (this is a phone call — keep responses under 2 sentences when possible)
- If the customer speaks Spanish, respond in Spanish
- If you cannot help, say: "Let me connect you with the owner" and set status=transfer
- Never make up information not provided above
- When booking, always confirm: service, date, time, and customer name + phone number
"""


def build_system_prompt(business: dict) -> str:
    services_text = ", ".join(
        f"{s['name']} (${s['price_usd']}, {s['duration_minutes']}min)"
        for s in business.get("services", [])
    )
    hours_text = ", ".join(
        f"{day}: {time}" for day, time in business.get("hours", {}).items()
    )
    return SYSTEM_PROMPT.format(
        business_name=business.get("name", "this business"),
        business_type=business.get("type", "salon"),
        hours=hours_text or "Please call during business hours",
        services=services_text or "Various services available",
    )


async def get_ai_response(
    messages: List[Message],
    business: dict,
    language: str = "en",
) -> str:
    system = build_system_prompt(business)
    if language == "es":
        system += "\n\nIMPORTANT: Respond ONLY in Spanish."

    history = [
        {"role": m.role, "parts": [m.content]}
        for m in messages[:-1]
    ]
    chat = _model.start_chat(history=history)

    last_message = messages[-1].content
    response = await chat.send_message_async(
        f"{system}\n\nCustomer: {last_message}"
        if not history
        else last_message
    )
    return response.text
