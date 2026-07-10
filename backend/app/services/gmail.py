import json
import base64
import logging
from typing import Dict, Any, Optional, List
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from app.config import settings

logger = logging.getLogger(__name__)


def get_gmail_service() -> Optional[Any]:
    """Helper to build and return the Gmail API client using parsed OAuth credentials."""
    if not settings.GMAIL_OAUTH_CREDENTIALS:
        logger.warning(
            "GMAIL_OAUTH_CREDENTIALS is not configured. Gmail API disabled."
        )
        return None

    try:
        creds_info = json.loads(settings.GMAIL_OAUTH_CREDENTIALS)
        # Parse credentials (handles access token, refresh token, client keys)
        creds = Credentials.from_authorized_user_info(creds_info)
        service = build("gmail", "v1", credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Failed to build Gmail service client: {e}")
        return None


async def send_email(to_email: str, subject: str, body: str) -> bool:
    """Sends an email reply to a recipient using Gmail API."""
    service = get_gmail_service()
    if not service:
        logger.warning("[STUB GMAIL] GMAIL_OAUTH_CREDENTIALS missing. Logging: "
                       f"To={to_email}, Subject={subject}, Body={body}")
        return False

    try:
        # Construct raw MIME message
        message = MIMEText(body)
        message["to"] = to_email
        message["subject"] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        # Send via API
        service.users().messages().send(
            userId="me", body={"raw": raw_message}
        ).execute()
        logger.info(f"Successfully sent email to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email via Gmail API: {e}")
        return False


def setup_watch(topic_name: str) -> Optional[Dict[str, Any]]:
    """Registers Gmail watch to publish push notifications to Google Pub/Sub topic."""
    service = get_gmail_service()
    if not service:
        return None

    try:
        request_body = {
            "labelIds": ["INBOX"],
            "topicName": topic_name,
        }
        watch_response = (
            service.users().watch(userId="me", body=request_body).execute()
        )
        logger.info(f"Gmail Watch established: {watch_response}")
        return watch_response
    except Exception as e:
        logger.error(f"Failed to setup Gmail Watch: {e}")
        return None


def get_new_emails(history_id: str) -> Optional[List[Dict[str, Any]]]:
    """Fetches details of new emails received since the given history_id."""
    service = get_gmail_service()
    if not service:
        return None

    try:
        # Retrieve mailbox history logs
        response = (
            service.users()
            .history()
            .list(userId="me", startHistoryId=history_id)
            .execute()
        )
        history_list = response.get("history", [])
        messages_to_process = []

        for history in history_list:
            messages_added = history.get("messagesAdded", [])
            for message_item in messages_added:
                msg_id = message_item.get("message", {}).get("id")
                if not msg_id:
                    continue

                # Fetch full message content
                msg_detail = (
                    service.users().messages().get(userId="me", id=msg_id).execute()
                )
                payload = msg_detail.get("payload", {})
                headers = payload.get("headers", [])

                # Extract From and Subject fields
                from_email = ""
                subject = ""
                for h in headers:
                    if h.get("name").lower() == "from":
                        from_email = h.get("value")
                    elif h.get("name").lower() == "subject":
                        subject = h.get("value")

                snippet = msg_detail.get("snippet", "")

                messages_to_process.append(
                    {
                        "message_id": msg_id,
                        "from": from_email,
                        "subject": subject,
                        "content": snippet,
                    }
                )

        return messages_to_process
    except Exception as e:
        logger.error(f"Failed to fetch new emails from history: {e}")
        return None
