import logging

logger = logging.getLogger(__name__)


async def send_email_stub(to_email: str, subject: str, body: str):
    logger.info(
        f"[STUB GMAIL] Sending email to {to_email} (Subject: {subject}): {body}"
    )
