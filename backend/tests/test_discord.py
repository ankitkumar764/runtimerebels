import unittest
from unittest.mock import patch, AsyncMock
from app.services.discord import send_message, send_typing_action


class TestDiscordService(unittest.TestCase):

    @patch("httpx.AsyncClient.post")
    @patch("app.config.settings.DISCORD_BOT_TOKEN", "mock_discord_token")
    def test_send_message_success(self, mock_post):
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Execute
        import asyncio

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            send_message("123456", "Hello from digital twin!")
        )

        self.assertTrue(result)
        mock_post.assert_called_once_with(
            "https://discord.com/api/v10/channels/123456/messages",
            headers={
                "Authorization": "Bot mock_discord_token",
                "Content-Type": "application/json",
            },
            json={"content": "Hello from digital twin!"},
            timeout=10.0,
        )

    @patch("httpx.AsyncClient.post")
    @patch("app.config.settings.DISCORD_BOT_TOKEN", "mock_discord_token")
    def test_send_typing_success(self, mock_post):
        mock_response = AsyncMock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        # Execute
        import asyncio

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(send_typing_action("123456"))

        self.assertTrue(result)
        mock_post.assert_called_once_with(
            "https://discord.com/api/v10/channels/123456/typing",
            headers={
                "Authorization": "Bot mock_discord_token",
                "Content-Type": "application/json",
            },
            timeout=5.0,
        )


if __name__ == "__main__":
    unittest.main()
