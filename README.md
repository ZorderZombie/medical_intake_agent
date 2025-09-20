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

Copy the ngrok public URL and use it when wiring OpenMic webhooks (next sections).

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
  ├── .venv                   # optional (for OPENMIC_API_KEY)
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


Note: In the JSON-backed version of routers/bots.py provided here, the API key is not required. You only need it if you later switch bots.py to call OpenMic’s REST API.

Paths to JSON files

Each service uses a path like:

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "<file>.json")


If your folder layout changes, update the DATA_PATH in:

routers/bots.py → data/bots.json

services/patients.py → data/patients.json

services/calls.py → data/calls.json

Data Files (JSON DB)
data/bots.json (sample)
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

data/patients.json (sample)
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

data/calls.json (starts empty)
[]

Run the server + ngrok

Start FastAPI:

uvicorn main:app --reload --port 3000


Start ngrok in another terminal:

ngrok http 3000


Copy the ngrok URL, e.g. https://random-subdomain.ngrok.io and use it for:

Pre-call webhook → https://<ngrok>/webhooks/pre-call

In-call function → https://<ngrok>/functions/fetch-patient

Post-call webhook → https://<ngrok>/webhooks/post-call

Swagger Testing (All Endpoints)

Open: http://127.0.0.1:3000/docs

Bots CRUD (JSON-backed)

Create (POST /bots)

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


List (GET /bots) → no body

Get (GET /bots/bot003) → no body

Update (PATCH /bots/bot003)

{
  "prompt": "You provide detailed dietary guidance, check for allergies, and suggest a weekly meal plan.",
  "voice": "verse"
}


Delete (DELETE /bots/bot002) → no body

In-call Function (POST /functions/fetch-patient)

Request

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

Pre-call Webhook (POST /webhooks/pre-call)

Request (what OpenMic will send)

{
  "event": "call",
  "call": {
    "sessionId": "sess_001",
    "from_number": "+919876543210",
    "to_number": "+911234567890",
    "attempt": 1
  }
}


Response (what you return)

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

Post-call Webhook (POST /webhooks/post-call)

Request (what OpenMic will send)

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


Response (what you return)

{
  "status": "ok"
}


What gets stored in calls.json

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

Create/Open your bot in OpenMic dashboard (or use their example bot).

In the bot’s Webhooks/Tools settings:

Pre-call webhook URL → https://<ngrok>/webhooks/pre-call

Custom Function (tool) → name it fetch_patient, method POST, URL https://<ngrok>/functions/fetch-patient

Post-call webhook URL → https://<ngrok>/webhooks/post-call

Click Test Call in OpenMic:

Agent introduces itself.

It asks for Medical ID.

You provide M123 → OpenMic calls your in-call function.

At end of call, OpenMic posts transcript/summary to your post-call webhook.

✅ Actual phone calls/mic input not required. The dashboard Test Call is sufficient.

Demo Script (for Loom)

Show http://127.0.0.1:3000/docs (Swagger).

Bots CRUD:

GET /bots → show seeded bots.

POST /bots → create bot003.

PATCH /bots/bot003 → update prompt/voice.

Functions:

POST /functions/fetch-patient with {"medical_id": "M123"} → show returned patient data.

Webhooks:

Show ngrok URL.

In OpenMic dashboard, run Test Call (with your URLs configured).

Show your server logs changing for pre-call → function → post-call.

Open data/calls.json and show saved transcript/summary/SOAP/risk.

Close with a quick recap.

Troubleshooting & Common Warnings
“⚠️ Warning: OPENMIC_API_KEY not set. Bot routes will fail.”

This prints if your code expects OPENMIC_API_KEY but it’s not set.

For the JSON-backed bots.py here, you don’t need the key.

If you switch to real OpenMic API calls, set the key via:

mac/linux: export OPENMIC_API_KEY=sk_...

windows powershell: $env:OPENMIC_API_KEY="sk_..."

or put it in .env and call load_dotenv() in main.py.

422 Unprocessable Entity in Swagger

Usually means invalid or extra fields or malformed JSON.

Ensure the request body matches the Swagger schema shown.

Always send valid JSON (double quotes, colons, commas, etc.).

Pre-call webhook timing out

OpenMic will time out if your endpoint doesn’t respond quickly.

Keep it lightweight: quick JSON lookup; return within ~1–3 seconds.

ngrok URL not working

Restart ngrok and update the URLs in the OpenMic dashboard.

Ensure you’re using https://... not http://... for webhooks.

Security Tips

Add a shared secret (e.g., X-Webhook-Token) and verify it on webhook requests.

Avoid storing raw PII; the example services/nlp.py shows simple redaction.

Log minimally in production (mask numbers, IDs).

Next Steps & Optional Upgrades

Switch bots CRUD to real OpenMic API using your OPENMIC_API_KEY.

Replace rule-based NLP with a small model or LLM call (for richer SOAP notes).

Add Pre-Tool webhook support for dynamic tool parameter injection.

Add basic auth or signature verification for webhooks.

Containerize with Docker & add CI.

Commands Reference
# run the server
uvicorn main:app --reload --port 3000

# run ngrok
ngrok http 3000

# set OPENMIC_API_KEY (bash/zsh)
export OPENMIC_API_KEY=sk_test_or_live_key_here

# set OPENMIC_API_KEY (powershell)
$env:OPENMIC_API_KEY="sk_test_or_live_key_here"
