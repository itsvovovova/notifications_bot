from contextlib import asynccontextmanager

import httpx
from fastapi import APIRouter, FastAPI, Request
from sqlalchemy_utils.utils import starts_with
from src.database.service import get_state
from src.services.service import register_user, get_score, change_mode, handler_login, handler_password
from src.config import get_settings
from httpx import AsyncClient

current_router = APIRouter()

async def set_telegram_webhook() -> None:
    async with AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{get_settings().BOT_TOKEN}/setWebhook",
            data={"url": get_settings().WEBHOOK_URL}
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    await set_telegram_webhook()
    yield

@current_router.post("/webhook", status_code=200)
async def telegram_webhook(request: Request) -> dict:
    data = await request.json()
    first_name = data.get("Chat").get("first_name")
    chat_id = data.get("Chat").get("chat_id")
    message = data.get("Message").get("text")

    if any(starts_with(message, prefix)
           for prefix in ["/start", "/score", "/mode"]):
        if starts_with(message, "/start"):
            response_text = await register_user(chat_id, first_name)
        elif starts_with(message, "/score"):
            response_text = await get_score(chat_id)
        elif starts_with(message, "/mode"):
            response_text = await change_mode(chat_id)
        await send_message(chat_id, response_text)
        return {"ok": True}

    current_state = get_state(chat_id)
    match current_state:
        case "login":
            response_text = await handler_login(chat_id, message)
            await send_message(chat_id, response_text)
        case "password":
            response_text = await handler_password(chat_id, message)
            await send_message(chat_id, response_text)
    return {"ok": True}


async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{get_settings().BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text
            }
        )













