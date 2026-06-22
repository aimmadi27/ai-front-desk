from fastapi import FastAPI
from app.api.routes import voice, sms, businesses, webhooks

app = FastAPI(title="AI Front Desk", version="0.1.0")

app.include_router(voice.router)
app.include_router(sms.router)
app.include_router(businesses.router)
app.include_router(webhooks.router)


@app.get("/health")
def health():
    return {"status": "ok"}
