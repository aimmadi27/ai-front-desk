from fastapi import APIRouter, HTTPException
from app.models.business import Business
from app.core.firestore import get_db
import uuid

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.post("/", response_model=Business)
def create_business(payload: Business):
    db = get_db()
    business_id = str(uuid.uuid4())
    payload.id = business_id
    db.collection("businesses").document(business_id).set(payload.model_dump())
    return payload


@router.get("/{business_id}", response_model=Business)
def get_business(business_id: str):
    db = get_db()
    doc = db.collection("businesses").document(business_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Business not found")
    return Business(**doc.to_dict())


@router.put("/{business_id}", response_model=Business)
def update_business(business_id: str, payload: Business):
    db = get_db()
    doc_ref = db.collection("businesses").document(business_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Business not found")
    payload.id = business_id
    doc_ref.set(payload.model_dump())
    return payload
