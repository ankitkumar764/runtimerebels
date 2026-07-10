import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.api.routes import app


class TestTelegramWebhook(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    @patch("app.api.webhooks.telegram.process_message_task.delay")
    def test_webhook_receives_and_queues(self, mock_celery_delay):
        # Sample update JSON payload representing a message sent to the bot
        payload = {
            "update_id": 987654321,
            "message": {
                "message_id": 12,
                "from": {
                    "id": 11223344,
                    "is_bot": False,
                    "first_name": "John",
                    "username": "johndoe",
                },
                "chat": {
                    "id": 11223344,
                    "first_name": "John",
                    "username": "johndoe",
                    "type": "private",
                },
                "date": 1782348920,
                "text": "What is my mom's name?",
            },
        }

        response = self.client.post("/webhook/telegram", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "queued"})

        # Verify celery task was triggered
        mock_celery_delay.assert_called_once_with(
            {
                "platform": "telegram",
                "sender_id": "11223344",
                "sender_name": "John",
                "content": "What is my mom's name?",
            }
        )

    def test_webhook_ignores_empty_message(self):
        payload = {
            "update_id": 987654321,
            # No message key, e.g. inline query or edited message
            "edited_message": {"message_id": 12},
        }

        response = self.client.post("/webhook/telegram", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ignored"})


if __name__ == "__main__":
    unittest.main()
