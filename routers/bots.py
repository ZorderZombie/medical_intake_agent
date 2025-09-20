# routers/bots.py
import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

# Path to bots.json (adjust if needed)
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bots.json")


# ----------------------
# Helpers to load/save JSON
# ----------------------
def _load_bots():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def _save_bots(bots):
    with open(DATA_PATH, "w") as f:
        json.dump(bots, f, indent=2)


# ----------------------
# Pydantic Models
# ----------------------
class BotBase(BaseModel):
    uid: str
    name: str
    prompt: str
    model: str = "gpt-4o-mini"
    voice: str = "alloy"
    status: str = "active"

class CreateBotRequest(BaseModel):
    name: str
    prompt: str
    model: str = "gpt-4o-mini"
    voice: str = "alloy"
    status: str = "active"

class UpdateBotRequest(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None
    model: Optional[str] = None
    voice: Optional[str] = None
    status: Optional[str] = None


# ----------------------
# Routes
# ----------------------
@router.get("/bots", response_model=List[BotBase])
async def list_bots():
    """List all bots from bots.json"""
    return _load_bots()


@router.get("/bots/{uid}", response_model=BotBase)
async def get_bot(uid: str):
    """Get a bot by UID"""
    bots = _load_bots()
    for b in bots:
        if b["uid"] == uid:
            return b
    raise HTTPException(status_code=404, detail="Bot not found")


@router.post("/bots", response_model=BotBase)
async def create_bot(bot: CreateBotRequest):
    """Create a new bot (saved into bots.json)"""
    bots = _load_bots()

    # Always generate new UID
    new_uid = f"bot{len(bots) + 1:03d}"

    new_bot = {
        "uid": new_uid,
        "name": bot.name,
        "prompt": bot.prompt,
        "model": bot.model,
        "voice": bot.voice,
        "status": bot.status,
    }

    bots.append(new_bot)
    _save_bots(bots)
    return new_bot


@router.patch("/bots/{uid}", response_model=BotBase)
async def update_bot(uid: str, updates: UpdateBotRequest):
    """Update an existing bot"""
    bots = _load_bots()
    for b in bots:
        if b["uid"] == uid:
            update_data = updates.dict(exclude_none=True)
            b.update(update_data)
            _save_bots(bots)
            return b
    raise HTTPException(status_code=404, detail="Bot not found")


@router.delete("/bots/{uid}")
async def delete_bot(uid: str):
    """Delete a bot"""
    bots = _load_bots()
    for i, b in enumerate(bots):
        if b["uid"] == uid:
            bots.pop(i)
            _save_bots(bots)
            return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Bot not found")
