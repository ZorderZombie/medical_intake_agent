# services/openmic.py
import os
import httpx

API_KEY = "omic_c88b60f1e3d7bfaad3deee5c5edde12ba726"
BASE_URL = "https://api.openmic.ai/v1"

headers = {"Authorization": f"Bearer {API_KEY}"}


async def create_bot(bot: dict) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/bots", headers=headers, json=bot)
        r.raise_for_status()
        return r.json()


async def list_bots() -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/bots", headers=headers)
        r.raise_for_status()
        return r.json()


async def get_bot(uid: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/bots/{uid}", headers=headers)
        r.raise_for_status()
        return r.json()


async def update_bot(uid: str, updates: dict) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.patch(f"{BASE_URL}/bots/{uid}", headers=headers, json=updates)
        r.raise_for_status()
        return r.json()


async def delete_bot(uid: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.delete(f"{BASE_URL}/bots/{uid}", headers=headers)
        r.raise_for_status()
        return {"status": "deleted"}
