from fastapi import APIRouter, Header, HTTPException
from app.services import reminders
from app.core.config import settings

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

# Cloud Scheduler hits these endpoints with a shared secret header
def _verify(token: str) -> None:
    if token != settings.scheduler_secret:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/reminders")
def run_reminders(x_scheduler_token: str = Header(...)):
    _verify(x_scheduler_token)
    sent = reminders.send_due_reminders()
    return {"sent": sent}


@router.post("/noshow-followup")
def run_noshow(x_scheduler_token: str = Header(...)):
    _verify(x_scheduler_token)
    sent = reminders.send_noshow_followups()
    return {"sent": sent}


@router.post("/reengagement")
def run_reengagement(x_scheduler_token: str = Header(...)):
    _verify(x_scheduler_token)
    sent = reminders.send_reengagement_messages()
    return {"sent": sent}
