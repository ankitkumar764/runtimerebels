import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

BASE_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


async def send_message(chat_id: str, text: str) -> bool:
    """Sends a text message to a specific Telegram chat via the Bot API."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning(
            "TELEGRAM_BOT_TOKEN is not configured. Cannot send message."
        )
        return False

    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            if response.status_code == 200:
                logger.info(f"Successfully sent Telegram message to {chat_id}")
                return True
            else:
                logger.error(
                    f"Telegram API error {response.status_code}: {response.text}"
                )
                return False
    except Exception as e:
        logger.error(f"Failed to connect to Telegram API: {e}")
        return False


async def send_typing_action(chat_id: str) -> bool:
    """Triggers the typing indicator action for a specific Telegram chat."""
    if not settings.TELEGRAM_BOT_TOKEN:
        return False

    url = f"{BASE_URL}/sendChatAction"
    payload = {"chat_id": chat_id, "action": "typing"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=5.0)
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Failed to send Telegram typing action: {e}")
        return False
