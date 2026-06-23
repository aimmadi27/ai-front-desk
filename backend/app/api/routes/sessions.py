from fastapi import APIRouter, HTTPException, Query
from app.core.firestore import get_db
from app.models.session import Session
from typing import List

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/", response_model=List[Session])
def list_sessions(business_id: str = Query(...)):
    db = get_db()
    docs = (
        db.collection("sessions")
        .where("business_id", "==", business_id)
        .order_by("call_sid")
        .stream()
    )
    return [Session(**d.to_dict()) for d in docs]


@router.get("/{call_sid}", response_model=Session)
def get_session(call_sid: str):
    db = get_db()
    doc = db.collection("sessions").document(call_sid).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Session not found")
    return Session(**doc.to_dict())
