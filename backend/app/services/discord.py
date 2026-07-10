import httpx
import logging
import discord
from app.config import settings

logger = logging.getLogger(__name__)

# Discord REST API Configurations
API_BASE_URL = "https://discord.com/api/v10"
HEADERS = {
    "Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}",
    "Content-Type": "application/json",
}


async def send_message(channel_id: str, text: str) -> bool:
    """Sends a message to a Discord channel using the REST API."""
    if not settings.DISCORD_BOT_TOKEN:
        logger.warning(
            "DISCORD_BOT_TOKEN is not configured. Cannot send message."
        )
        return False

    url = f"{API_BASE_URL}/channels/{channel_id}/messages"
    payload = {"content": text}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=HEADERS, json=payload, timeout=10.0)
            if response.status_code == 200 or response.status_code == 201:
                logger.info(f"Successfully sent Discord message to {channel_id}")
                return True
            else:
                logger.error(
                    f"Discord REST API error {response.status_code}: {response.text}"
                )
                return False
    except Exception as e:
        logger.error(f"Failed to connect to Discord REST API: {e}")
        return False


async def send_typing_action(channel_id: str) -> bool:
    """Triggers the typing indicator in a Discord channel using the REST API."""
    if not settings.DISCORD_BOT_TOKEN:
        return False

    url = f"{API_BASE_URL}/channels/{channel_id}/typing"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=HEADERS, timeout=5.0)
            return response.status_code == 204
    except Exception as e:
        logger.error(f"Failed to send Discord typing action: {e}")
        return False


# Setup Gateway Client (Runs in FastAPI process to listen for messages)
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot_client = discord.Client(intents=intents)


@bot_client.event
async def on_ready():
    logger.info(f"Discord Bot connected to Gateway as: {bot_client.user}")


@bot_client.event
async def on_message(message):
    # Ignore own messages to avoid infinite loops
    if message.author == bot_client.user:
        return

    # Ignore system messages or messages without content
    if not message.content or message.author.bot:
        return

    logger.info(
        f"Received Discord message from {message.author.name} (Channel: {message.channel.id}): {message.content}"
    )

    # Queue message processing to Celery background task
    from app.workers.tasks import process_message_task

    incoming_payload = {
        "platform": "discord",
        "sender_id": str(message.channel.id),
        "sender_name": message.author.name,
        "content": message.content,
    }

    process_message_task.delay(incoming_payload)
    logger.info(
        f"Queued Discord message from {message.author.name} to Celery workers."
    )
