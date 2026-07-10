import logging

logger = logging.getLogger(__name__)


async def send_message_stub(channel_id: str, text: str):
    logger.info(f"[STUB DISCORD] Sending message to {channel_id}: {text}")


async def trigger_typing_stub(channel_id: str):
    logger.info(f"[STUB DISCORD] Triggering typing indicator for {channel_id}")
