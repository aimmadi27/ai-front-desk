from googleapiclient.discovery import build
from google.auth import default
from datetime import datetime, timedelta
from typing import List, Optional


def get_calendar_service():
    creds, _ = default(scopes=["https://www.googleapis.com/auth/calendar"])
    return build("calendar", "v3", credentials=creds)


def get_available_slots(
    calendar_id: str,
    date: str,  # YYYY-MM-DD
    duration_minutes: int = 60,
) -> List[str]:
    service = get_calendar_service()
    day_start = datetime.fromisoformat(f"{date}T09:00:00")
    day_end = datetime.fromisoformat(f"{date}T18:00:00")

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=day_start.isoformat() + "Z",
        timeMax=day_end.isoformat() + "Z",
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    busy = events_result.get("items", [])

    busy_ranges = [
        (
            datetime.fromisoformat(e["start"].get("dateTime", e["start"].get("date"))),
            datetime.fromisoformat(e["end"].get("dateTime", e["end"].get("date"))),
        )
        for e in busy
    ]

    slots = []
    current = day_start
    while current + timedelta(minutes=duration_minutes) <= day_end:
        slot_end = current + timedelta(minutes=duration_minutes)
        if not any(s < slot_end and current < e for s, e in busy_ranges):
            slots.append(current.strftime("%I:%M %p"))
        current += timedelta(minutes=30)

    return slots


def book_appointment(
    calendar_id: str,
    customer_name: str,
    customer_phone: str,
    service: str,
    start_datetime: str,  # ISO format
    duration_minutes: int,
) -> Optional[str]:
    service_cal = get_calendar_service()
    start = datetime.fromisoformat(start_datetime)
    end = start + timedelta(minutes=duration_minutes)

    event = {
        "summary": f"{service} — {customer_name}",
        "description": f"Customer phone: {customer_phone}",
        "start": {"dateTime": start.isoformat(), "timeZone": "America/New_York"},
        "end": {"dateTime": end.isoformat(), "timeZone": "America/New_York"},
    }

    created = service_cal.events().insert(calendarId=calendar_id, body=event).execute()
    return created.get("id")
