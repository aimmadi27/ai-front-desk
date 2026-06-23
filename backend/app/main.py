from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import voice, sms, businesses, webhooks, sessions, stats, scheduler, chat

app = FastAPI(title="AI Front Desk", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice.router)
app.include_router(sms.router)
app.include_router(businesses.router)
app.include_router(webhooks.router)
app.include_router(sessions.router)
app.include_router(stats.router)
app.include_router(scheduler.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}
