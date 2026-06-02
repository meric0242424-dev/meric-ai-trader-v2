import httpx
from app.core.config import settings

async def telegram_send(text: str):
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return False
    url=f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=10) as c:
        await c.post(url, json={"chat_id": settings.telegram_chat_id, "text": text})
    return True
