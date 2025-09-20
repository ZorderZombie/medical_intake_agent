# routers/webhooks.py
import uuid
from fastapi import APIRouter
from services import patients, calls, nlp

router = APIRouter()


@router.post("/webhooks/pre-call")
async def pre_call_webhook(payload: dict):
    """
    OpenMic calls this before the call begins.
    Returns patient details as dynamic variables if found.
    """
    call = payload.get("call", {})
    from_number = call.get("from_number")

    patient = patients.lookup_by_phone(from_number)
    if not patient:
        return {"call": {"dynamic_variables": {}}}

    return {
        "call": {
            "dynamic_variables": {
                "patient_name": patient["name"],
                "medical_id": patient["medical_id"],
                "allergies": patient["allergies"],
                "conditions": patient["conditions"],
                "last_visit": patient["last_visit"],
            }
        }
    }


@router.post("/webhooks/post-call")
async def post_call_webhook(payload: dict):
    """
    OpenMic calls this after the call ends.
    - Runs NLP (redaction, SOAP, risk).
    - Upserts into calls.json (update if session exists, insert if new).
    """

    # Normalize session_id
    session_id = payload.get("sessionId") or payload.get("session_id")
    if not session_id:
        session_id = f"auto_{uuid.uuid4().hex[:8]}"

    transcript = payload.get("transcript", "")
    summary = payload.get("summary", "")
    bot_uid = payload.get("bot_uid")

    # Run NLP safely
    try:
        redacted = nlp.redact(transcript)
        soap = nlp.soapify(transcript, summary)
        risk = nlp.classify_risk(transcript)
    except Exception:
        redacted, soap, risk = transcript, {}, "unknown"

    # Build new record
    record = {
        "session_id": session_id,
        "bot_uid": bot_uid,
        "transcript": transcript,
        "redacted_transcript": redacted,
        "summary": summary,
        "soap": soap,
        "risk": risk,
        "is_successful": payload.get("isSuccessful", False),
        "started_at": payload.get("startedAt"),
        "ended_at": payload.get("endedAt"),
    }

    updated, total = calls.upsert(record)

    return {
        "status": "ok",
        "session_id": session_id,
        "updated": updated,
        "total_records": total,
    }
