# AI Front Desk

AI-powered front desk agent for local service businesses. Handles calls, SMS, and web chat — books appointments, answers FAQs, sends reminders — 24/7.

Built for the **Build with Gemini XPRIZE** hackathon | Deadline: August 17, 2026

---

## Stack

| Layer | Tool |
|---|---|
| AI | Gemini 2.5 Flash |
| Orchestration | Vertex AI Agent Builder |
| Voice/SMS | Twilio |
| Speech | Google STT / TTS |
| Backend | FastAPI on Cloud Run |
| Database | Firestore |
| Dashboard | Next.js on Vercel |

---

## Project Structure

```
ai-front-desk/
├── backend/          # FastAPI — voice, SMS, webhooks, business API
│   ├── app/
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   └── tests/
├── dashboard/        # Next.js — business owner portal
└── infra/            # Cloud Run + Firestore config
```

---

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
uvicorn app.main:app --reload
```

### Expose to Twilio (local dev)

```bash
ngrok http 8000
# Set Twilio webhook to: https://<ngrok-url>/voice/incoming
```

### Run tests

```bash
cd backend
pytest tests/ -v
```

---

## Environment Variables

See `backend/.env.example` for all required keys.

---

## Submission Deadline

**August 17, 2026 at 1:00pm PDT** on Devpost
