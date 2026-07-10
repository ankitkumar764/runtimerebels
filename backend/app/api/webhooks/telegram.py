from fastapi import APIRouter, Request, HTTPException
import logging
from app.workers.tasks import process_message_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("")
async def telegram_webhook(request: Request):
    """Webhook endpoint to receive updates from Telegram Bot API."""
    try:
        update = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse incoming webhook JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    logger.info(f"Received Telegram webhook update: {update}")

    # Check if update contains a message
    message = update.get("message")
    if not message:
        # We acknowledge updates that are not messages (e.g. edits, inline queries) but skip processing
        return {"status": "ignored"}

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text")
    from_user = message.get("from", {})
    first_name = from_user.get("first_name", "User")

    if not chat_id or not text:
        logger.warning("Received Telegram message without chat_id or text. Ignoring.")
        return {"status": "ignored"}

    # Convert to schema payload dictionary for Celery background tasks
    incoming_payload = {
        "platform": "telegram",
        "sender_id": str(chat_id),
        "sender_name": first_name,
        "content": text,
    }

    # Offload message logic execution path to background queue
    process_message_task.delay(incoming_payload)
    logger.info(f"Queued message from {first_name} ({chat_id}) to Celery workers.")

    return {"status": "queued"}
