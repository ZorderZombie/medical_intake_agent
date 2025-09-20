# Medical Intake Agent (Backend + Webhooks) — FastAPI + JSON DB

Build a **domain-specific AI intake agent** for the **Medical** use-case using **OpenMic**.  
This repository contains only the **backend** (no UI) and demonstrates:

- **Pre-call webhook** → enrich call with patient context  
- **In-call function** → fetch patient by Medical ID  
- **Post-call webhook** → receive transcript/summary, run lightweight NLP, store results  
- **Bot CRUD** → create/list/update/delete bots (stored in local `data/bots.json` for easy testing)  
- **Swagger UI** for local testing  
- **ngrok** integration so OpenMic can reach your local webhooks during a Test Call  

> ✅ **No real phone calls or mic input are required.** Use OpenMic **Test Call** in their dashboard.  

---

## Table of Contents

1. [Prerequisites](#prerequisites)  
2. [Quick Start](#quick-start)  
3. [Project Structure](#project-structure)  
4. [Configuration](#configuration)  
5. [Data Files (JSON DB)](#data-files-json-db)  
6. [Run the server + ngrok](#run-the-server--ngrok)  
7. [Swagger Testing (All Endpoints)](#swagger-testing-all-endpoints)  
8. [OpenMic Dashboard Wiring](#openmic-dashboard-wiring)  
9. [Demo Script (for Loom)](#demo-script-for-loom)  
10. [Troubleshooting & Common Warnings](#troubleshooting--common-warnings)  
11. [Security Tips](#security-tips)  
12. [Next Steps & Optional Upgrades](#next-steps--optional-upgrades)  

---

## Prerequisites

- **Python 3.10+**  
- **pip** (or uv/poetry if you prefer)  
- **ngrok** (or any HTTPS tunneling tool)  
- An **OpenMic** account + API key (optional if you only use local JSON bots)  
  - Sign up & key creation are noted in [OpenMic Dashboard Wiring](#openmic-dashboard-wiring).  

---

## Quick Start

```bash
git clone <your-repo-url>
cd medical_intake_agent

# 1) create and activate a venv (recommended)
python -m venv .venv
source .venv/bin/activate        # mac/linux
# .venv\Scripts\activate         # windows

# 2) install deps
pip install fastapi uvicorn httpx python-dotenv

# 3) run the api
uvicorn main:app --reload --port 3000

# 4) in a separate terminal, start ngrok
ngrok http 3000

Open Swagger at: http://127.0.0.1:3000/docs

Copy the ngrok public URL and use it when wiring OpenMic webhooks.

Project Structure

medical_intake_agent/
  ├── main.py
  ├── routers/
  │    ├── webhooks.py       # pre-call & post-call
  │    ├── functions.py      # in-call function fetch-patient
  │    └── bots.py           # bots CRUD (JSON-backed)
  ├── services/
  │    ├── patients.py       # JSON read helpers for patients
  │    ├── calls.py          # JSON read/write helpers for calls
  │    └── nlp.py            # redaction, SOAP generation, risk rules
  ├── data/
  │    ├── bots.json
  │    ├── patients.json
  │    └── calls.json
  ├── .env                   # optional (for OPENMIC_API_KEY)
  └── README.md

Configuration
Environment Variables

If you later proxy real OpenMic Bot CRUD (instead of local JSON), set:
# mac/linux (bash/zsh)
export OPENMIC_API_KEY=sk_test_or_live_key_here

# windows powershell
$env:OPENMIC_API_KEY="sk_test_or_live_key_here"

Or use .env:
OPENMIC_API_KEY=sk_test_or_live_key_here

In main.py:
from dotenv import load_dotenv
load_dotenv()

Note: In the JSON-backed version of routers/bots.py, the API key is not required.

Paths to JSON files

Each service uses a path like:
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "<file>.json")


Update if your folder layout changes:

routers/bots.py → data/bots.json

services/patients.py → data/patients.json

services/calls.py → data/calls.json

Data Files (JSON DB)
data/bots.json

[
  {
    "uid": "bot001",
    "name": "Medical Intake Bot",
    "prompt": "You are a medical intake assistant. Greet the patient, verify their ID, ask about allergies and conditions, and ensure safe intake.",
    "model": "gpt-4o-mini",
    "voice": "alloy",
    "status": "active"
  },
  {
    "uid": "bot002",
    "name": "Follow-up Reminder Bot",
    "prompt": "You remind patients about follow-up appointments and check if they have new symptoms.",
    "model": "gpt-4o-mini",
    "voice": "verse",
    "status": "active"
  }
]

data/patients.json

[
  {
    "medical_id": "M123",
    "name": "Anita Rao",
    "phone": "+919876543210",
    "dob": "1992-06-11",
    "allergies": ["Penicillin"],
    "conditions": ["Type 2 Diabetes"],
    "last_visit": "2025-08-09",
    "notes": "On metformin, stable"
  }
]

data/calls.json
[]

Run the server + ngrok
# run FastAPI
uvicorn main:app --reload --port 3000

# run ngrok in another terminal
ngrok http 3000


Use the ngrok URL for webhooks:

Pre-call → https://<ngrok>/webhooks/pre-call

In-call function → https://<ngrok>/functions/fetch-patient

Post-call → https://<ngrok>/webhooks/post-call

Swagger Testing (All Endpoints)

Open: http://127.0.0.1:3000/docs

Bots CRUD

POST /bots
{
  "name": "Diet Consultation Bot",
  "prompt": "You provide dietary advice and record patient food allergies.",
  "model": "gpt-4o-mini",
  "voice": "calm",
  "status": "active"
}

Response
{
  "uid": "bot003",
  "name": "Diet Consultation Bot",
  "prompt": "You provide dietary advice and record patient food allergies.",
  "model": "gpt-4o-mini",
  "voice": "calm",
  "status": "active"
}

PATCH /bots/bot003

{
  "prompt": "You provide detailed dietary guidance, check for allergies, and suggest a weekly meal plan.",
  "voice": "verse"
}

In-call Function

POST /functions/fetch-patient

{
  "medical_id": "M123"
}


Response

{
  "medical_id": "M123",
  "name": "Anita Rao",
  "dob": "1992-06-11",
  "allergies": ["Penicillin"],
  "conditions": ["Type 2 Diabetes"],
  "last_visit": "2025-08-09",
  "notes": "On metformin, stable"
}

Pre-call Webhook

POST /webhooks/pre-call

Request:

{
  "event": "call",
  "call": {
    "sessionId": "sess_001",
    "from_number": "+919876543210",
    "to_number": "+911234567890",
    "attempt": 1
  }
}


Response:

{
  "call": {
    "dynamic_variables": {
      "patient_name": "Anita Rao",
      "medical_id": "M123",
      "allergies": ["Penicillin"],
      "conditions": ["Type 2 Diabetes"],
      "last_visit": "2025-08-09"
    }
  }
}

Post-call Webhook

POST /webhooks/post-call

Request:

{
  "type": "end-of-call-report",
  "sessionId": "sess_001",
  "bot_uid": "bot001",
  "transcript": "Patient reported chest pain for two days.",
  "summary": "Possible angina. Needs urgent check-up.",
  "isSuccessful": true,
  "startedAt": "2025-09-20T10:00:00Z",
  "endedAt": "2025-09-20T10:05:00Z"
}


Response:

{
  "status": "ok"
}


Stored in calls.json:

[
  {
    "session_id": "sess_001",
    "bot_uid": "bot001",
    "transcript": "Patient reported chest pain for two days.",
    "redacted_transcript": "Patient reported chest pain for two days.",
    "summary": "Possible angina. Needs urgent check-up.",
    "soap": {
      "S": "Patient reported chest pain for two days.",
      "O": "Vitals not captured",
      "A": "Possible angina. Needs urgent check-up.",
      "P": "Follow-up in 2 days"
    },
    "risk": "urgent"
  }
]

OpenMic Dashboard Wiring

Create a bot in OpenMic dashboard.

Configure:

Pre-call webhook → https://<ngrok>/webhooks/pre-call

Custom Function → https://<ngrok>/functions/fetch-patient

Post-call webhook → https://<ngrok>/webhooks/post-call

Run a Test Call to see the flow end-to-end.

Demo Script (for Loom)

Show Swagger (http://127.0.0.1:3000/docs).

CRUD bots (create, update, list).

Call POST /functions/fetch-patient with M123.

Run Test Call in OpenMic → watch pre-call → in-call → post-call.

Show updated calls.json.

Troubleshooting & Common Warnings

⚠️ OPENMIC_API_KEY not set → safe to ignore if using JSON DB.

422 Validation Error → check your JSON matches schema.

Webhook timeout → ensure fast responses (<3s).

ngrok URL not working → restart ngrok and update dashboard URLs.

Security Tips

Add X-Webhook-Token header validation.

Redact PII in transcripts.

Avoid logging sensitive info.

Next Steps & Optional Upgrades

Use OpenMic API for real bot CRUD.

Replace rule-based NLP with small LLM.

Add Pre-Tool webhook.

Containerize with Docker.

Commands Reference
uvicorn main:app --reload --port 3000
ngrok http 3000

# set OPENMIC_API_KEY
export OPENMIC_API_KEY=sk_test_or_live_key_here   # mac/linux
$env:OPENMIC_API_KEY="sk_test_or_live_key_here"   # windows