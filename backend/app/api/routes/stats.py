from fastapi import APIRouter, Query
from app.core.firestore import get_db
from datetime import datetime, timezone

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/")
def get_stats(business_id: str = Query(...)):
    db = get_db()
    sessions = list(
        db.collection("sessions")
        .where("business_id", "==", business_id)
        .stream()
    )

    today = datetime.now(timezone.utc).date().isoformat()
    this_month = datetime.now(timezone.utc).strftime("%Y-%m")

    calls_today = 0
    bookings_today = 0
    calls_this_month = 0
    bookings_this_month = 0
    missed_calls = 0

    for doc in sessions:
        data = doc.to_dict()
        created = data.get("created_at", "")
        messages = data.get("messages", [])
        status = data.get("status", "")

        if created.startswith(today):
            calls_today += 1
            if any("confirm" in m.get("content", "").lower() for m in messages if m.get("role") == "model"):
                bookings_today += 1

        if created.startswith(this_month):
            calls_this_month += 1
            if any("confirm" in m.get("content", "").lower() for m in messages if m.get("role") == "model"):
                bookings_this_month += 1

        if status == "missed":
            missed_calls += 1

    return {
        "calls_today": calls_today,
        "bookings_today": bookings_today,
        "calls_this_month": calls_this_month,
        "bookings_this_month": bookings_this_month,
        "missed_calls": missed_calls,
    }
