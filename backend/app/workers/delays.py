import random
import logging
from app.config import settings

logger = logging.getLogger(__name__)


def calculate_typing_delay(reply_text: str) -> float:
    """Calculates human-like response delay based on text length and random jitter."""
    if not reply_text:
        return 0.0

    # Human typing speed simulation: (chars / 10) * 0.8 seconds + random jitter
    base_delay = (len(reply_text) / 10.0) * 0.8
    jitter = random.uniform(0.2, 2.0)
    total_delay = base_delay + jitter

    # Clamp the delay between user configured minimum and maximum limits
    min_delay = settings.REPLY_DELAY_MIN
    max_delay = settings.REPLY_DELAY_MAX

    # Clamp logic
    clamped_delay = max(min_delay, min(total_delay, max_delay))

    logger.info(
        f"Calculated typing delay for response ({len(reply_text)} chars): "
        f"Base={base_delay:.2f}s, Jitter={jitter:.2f}s, Final Clamped={clamped_delay:.2f}s"
    )

    return clamped_delay


def calculate_bubble_delay() -> float:
    """Returns the delay between successive message bubble splits (400ms)."""
    return 0.4
