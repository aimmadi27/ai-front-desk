import stripe
from fastapi import APIRouter, Header, HTTPException, Request
from app.core.config import settings
from app.core.firestore import get_db

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

stripe.api_key = settings.stripe_secret_key


@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(...)):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.stripe_webhook_secret
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "customer.subscription.created":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        _activate_business(customer_id)

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        _deactivate_business(customer_id)

    return {"status": "ok"}


def _activate_business(stripe_customer_id: str) -> None:
    db = get_db()
    docs = db.collection("businesses").where("stripe_customer_id", "==", stripe_customer_id).stream()
    for doc in docs:
        doc.reference.update({"active": True})


def _deactivate_business(stripe_customer_id: str) -> None:
    db = get_db()
    docs = db.collection("businesses").where("stripe_customer_id", "==", stripe_customer_id).stream()
    for doc in docs:
        doc.reference.update({"active": False})
