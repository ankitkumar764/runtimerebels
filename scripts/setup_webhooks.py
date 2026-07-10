import os
import sys
import urllib.request
import urllib.parse
import json

# Ensure parent directory is in path to load app configs if run directly
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"
    )
)

from app.config import settings

# Or simply read directly from env using dotenv if sys.path loading fails
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or settings.TELEGRAM_BOT_TOKEN
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE_URL") or settings.WEBHOOK_BASE_URL


def setup_telegram_webhook():
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment configurations.")
        return

    if not WEBHOOK_BASE or "your-ngrok" in WEBHOOK_BASE:
        print("Error: WEBHOOK_BASE_URL is not set to a valid public URL.")
        return

    webhook_url = f"{WEBHOOK_BASE}/webhook/telegram"
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"

    print(f"Registering Telegram webhook for URL: {webhook_url}...")

    # Set up request payload
    data = urllib.parse.urlencode({"url": webhook_url}).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, method="POST")

    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            if res_json.get("ok"):
                print(
                    f"Success! Webhook registered successfully: {res_json.get('description')}"
                )
            else:
                print(f"Failed to register webhook: {res_body}")
    except Exception as e:
        print(f"Connection error occurred during API request: {e}")


if __name__ == "__main__":
    setup_telegram_webhook()
