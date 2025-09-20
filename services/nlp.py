# services/nlp.py
import re
from typing import Dict

# Redact sensitive info (phones, names "Rahul", etc.)
def redact(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\b\d{10}\b", "[PHONE]", text)
    text = re.sub(r"\b(Rahul|Anita|Meera)\b", "[NAME]", text, flags=re.IGNORECASE)
    return text


def soapify(transcript: str, summary: str) -> Dict[str, str]:
    if not transcript:
        return {"S": "", "O": "", "A": "", "P": ""}
    sentences = transcript.split(".")
    subjective = sentences[0] if sentences else transcript
    return {
        "S": subjective.strip(),
        "O": "No vitals captured.",
        "A": summary.strip() if summary else "No assessment.",
        "P": "Follow-up recommended."
    }


def classify_risk(text: str) -> str:
    if not text:
        return "routine"
    if "chest pain" in text.lower() or "shortness of breath" in text.lower():
        return "urgent"
    if "fever" in text.lower():
        return "moderate"
    return "routine"
