# routers/webhooks.py
from fastapi import APIRouter, HTTPException
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
        # If no patient match, let the call proceed with empty variables
        return {"call": {"dynamic_variables": {}}}

    return {
        "call": {
            "dynamic_variables": {
                "patient_name": patient["name"],
                "medical_id": patient["medical_id"],
                "allergies": patient["allergies"],
                "conditions": patient["conditions"],
                "last_visit": patient["last_visit"]
            }
        }
    }


@router.post("/webhooks/post-call")
async def post_call_webhook(payload: dict):
    """
    OpenMic calls this after the call ends.
    We save call transcript, run redaction, SOAP notes, and risk classification.
    """
    session_id = payload.get("sessionId")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing sessionId")

    transcript = payload.get("transcript", "")
    summary = payload.get("summary", "")

    # Run NLP utilities
    redacted = nlp.redact(transcript)
    soap = nlp.soapify(transcript, summary)
    risk = nlp.classify_risk(transcript)

    # Save call log
    calls.store({
        "session_id": session_id,
        "bot_uid": payload.get("bot_uid"),
        "transcript": transcript,
        "redacted_transcript": redacted,
        "summary": summary,
        "soap": soap,
        "risk": risk
    })

    return {"status": "ok"}
