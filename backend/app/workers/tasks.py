import asyncio
import time
import logging
from typing import Dict, Any
from app.workers.celery_app import celery_app
from app.workers.delays import calculate_typing_delay, calculate_bubble_delay
from app.core.router import graph
from app.services.telegram import send_message as tg_send, send_typing_action as tg_type
from app.services.discord import send_message as ds_send, send_typing_action as ds_type
from app.services.gmail import send_email_stub as gm_send

logger = logging.getLogger(__name__)


@celery_app.task(name="process_message_task")
def process_message_task(message_data: Dict[str, Any]):
    """Processes incoming message in the background, simulates typing delay, and sends reply."""
    logger.info(f"Received message task for background processing: {message_data}")

    platform = message_data.get("platform")
    sender_id = message_data.get("sender_id")
    sender_name = message_data.get("sender_name")
    content = message_data.get("content")

    # 1. Run LangGraph pipeline to generate response (run async in sync celery context)
    async def run_ai_pipeline():
        inputs = {
            "query": content,
            "sender_id": sender_id,
            "route": "",
            "evidence": "",
            "confidence": 0.0,
            "raw_response": "",
            "final_response": [],
        }
        return await graph.ainvoke(inputs)

    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    result = loop.run_until_complete(run_ai_pipeline())
    bubbles = result.get("final_response", [])

    if not bubbles:
        logger.warning("AI pipeline generated no bubbles. Skipping response.")
        return

    # Combine text to calculate typing delay
    combined_response = " ".join(bubbles)
    typing_delay = calculate_typing_delay(combined_response)

    # 2. Trigger "typing..." status indicator on target platform (non-blocking)
    try:
        if platform == "telegram":
            loop.run_until_complete(tg_type(sender_id))
        elif platform == "discord":
            loop.run_until_complete(ds_type(sender_id))
    except Exception as e:
        logger.error(f"Failed to trigger typing status: {e}")

    # 3. Simulate human typing delay
    logger.info(f"Simulating human typing delay of {typing_delay:.2f}s...")
    time.sleep(typing_delay)

    # 4. Dispatch reply bubbles with split-bubble interval delays
    bubble_delay = calculate_bubble_delay()

    for idx, bubble in enumerate(bubbles):
        if idx > 0:
            logger.info(f"Waiting {bubble_delay}s between bubble splits...")
            time.sleep(bubble_delay)

        logger.info(f"Dispatching bubble {idx+1}/{len(bubbles)}: {bubble}")

        try:
            if platform == "telegram":
                loop.run_until_complete(tg_send(sender_id, bubble))
            elif platform == "discord":
                loop.run_until_complete(ds_send(sender_id, bubble))
            elif platform == "gmail":
                subject = "Re: Digital Twin Autopilot"
                loop.run_until_complete(gm_send(sender_id, subject, bubble))
        except Exception as e:
            logger.error(f"Failed to send bubble to {platform}: {e}")

    logger.info("Message processing and dispatch completed successfully.")
