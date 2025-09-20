# routers/functions.py
from fastapi import APIRouter, HTTPException
from services import patients

router = APIRouter()


@router.post("/functions/fetch-patient")
async def fetch_patient(payload: dict):
    """
    Agent asks for a medical ID, we return patient info.
    This endpoint is configured in OpenMic dashboard as a custom function.
    """
    medical_id = payload.get("medical_id")
    if not medical_id:
        raise HTTPException(status_code=400, detail="medical_id required")

    patient = patients.lookup_by_id(medical_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {
        "medical_id": patient["medical_id"],
        "name": patient["name"],
        "dob": patient["dob"],
        "allergies": patient["allergies"],
        "conditions": patient["conditions"],
        "last_visit": patient["last_visit"],
        "notes": patient.get("notes", "")
    }
