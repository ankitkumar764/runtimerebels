import logging

logger = logging.getLogger(__name__)


async def send_message_stub(chat_id: str, text: str):
    logger.info(f"[STUB TELEGRAM] Sending message to {chat_id}: {text}")


async def trigger_typing_stub(chat_id: str):
    logger.info(f"[STUB TELEGRAM] Triggering typing indicator for {chat_id}")
