import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from execution.telegram_service import TelegramService


class TestTelegramService(unittest.TestCase):
    @patch.dict(
        os.environ, {"TELEGRAM_BOT_TOKEN": "fake_token", "TELEGRAM_CHAT_ID": "12345"}
    )
    @patch("execution.telegram_service.telebot.TeleBot")
    def setUp(self, MockTeleBot):
        self.mock_bot = MockTeleBot.return_value
        self.service = TelegramService()

    def test_sanitize_markdown(self):
        text = "Hello. World! (Test)"
        expected = "Hello\\. World\\! \\(Test\\)"
        self.assertEqual(self.service.sanitize_markdown(text), expected)

        text_all = "_*[]()~`>#+-=|{}.!"
        expected_all = "".join([f"\\{c}" for c in text_all])
        self.assertEqual(self.service.sanitize_markdown(text_all), expected_all)

    def test_send_photo(self):
        url = "http://example.com/photo.jpg"
        caption = "Look at this!"
        expected_caption = "Look at this\\!"

        self.service.send_photo(url, caption)

        self.mock_bot.send_photo.assert_called_with(
            "12345", url, caption=expected_caption, parse_mode="MarkdownV2"
        )

    def test_send_video(self):
        url = "http://example.com/video.mp4"
        caption = "Watch this video."
        expected_caption = "Watch this video\\."

        self.service.send_video(url, caption)

        self.mock_bot.send_video.assert_called_with(
            "12345", url, caption=expected_caption, parse_mode="MarkdownV2"
        )

    def test_send_youtube(self):
        url = "http://youtube.com/watch?v=123"
        text = "Check out this video!"
        expected_text = "Check out this video\\!"

        self.service.send_youtube(url, text)

        # Expect message to be text + newline + url
        expected_message = f"{expected_text}\n{url}"

        self.mock_bot.send_message.assert_called_with(
            "12345", expected_message, parse_mode="MarkdownV2"
        )


if __name__ == "__main__":
    unittest.main()
