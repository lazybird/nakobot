import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from execution.sheets_service import SheetsService
import main


class TestOrchestration(unittest.TestCase):
    @patch("execution.sheets_service.gspread")
    @patch("execution.sheets_service.Credentials")
    @patch.dict(
        os.environ,
        {
            "GREETS_SERVICE_ACCOUNT_JSON": "eyJrZXkiOiJ2YWx1ZSJ9",  # Base64 encoded JSON
            "GOOGLE_SHEET_ID": "fake_id",
            "TELEGRAM_BOT_TOKEN": "fake_token",
            "TELEGRAM_CHAT_ID": "12345",
        },
    )
    def test_get_due_tasks_dynamic_columns(self, MockCredentials, MockGspread):
        # Mock Sheets API response
        mock_sheet = MagicMock()
        MockGspread.authorize.return_value.open_by_key.return_value.sheet1 = mock_sheet

        today = datetime.now().strftime("%Y-%m-%d")

        # Scenario: Header with mixed case and specific order
        mock_sheet.get_all_values.return_value = [
            ["Date d'envoi", "Type", "Contenu Message", "Statut"],
            [today, "image", "http://img.com", "À envoyer"],
            [today, "video", "http://vid.com", "À envoyer"],
            [today, "", "Just text", "À envoyer"],  # Empty type -> text
            ["2025-01-01", "text", "Old", "À envoyer"],  # Wrong date
            [today, "text", "Done", "Envoyé"],  # Wrong status
        ]

        service = SheetsService()
        tasks = service.get_due_tasks()

        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0]["type"], "image")
        self.assertEqual(tasks[0]["content"], "http://img.com")
        self.assertEqual(tasks[1]["type"], "video")
        self.assertEqual(tasks[2]["type"], "text")

    @patch("main.TelegramService")
    @patch("main.SheetsService")
    def test_main_dispatch(self, MockSheets, MockTelegram):
        # Setup mocks
        mock_sheets_instance = MockSheets.return_value
        mock_telegram_instance = MockTelegram.return_value

        mock_sheets_instance.get_due_tasks.return_value = [
            {"row": 2, "type": "image", "content": "http://img.com", "status_col": 4},
            {"row": 3, "type": "video", "content": "http://vid.com", "status_col": 4},
            {"row": 4, "type": "youtube", "content": "http://yt.com", "status_col": 4},
            {"row": 5, "type": "text", "content": "Hello", "status_col": 4},
        ]

        # Run main
        main.main()

        # Verify calls
        mock_telegram_instance.send_photo.assert_called_with("http://img.com")
        mock_telegram_instance.send_video.assert_called_with("http://vid.com")
        mock_telegram_instance.send_youtube.assert_called_with("http://yt.com")
        mock_telegram_instance.send_message.assert_called_with("Hello")

        # Verify updates (check that the second arg is 4)
        mock_sheets_instance.mark_as_sent.assert_any_call(2, 4)
        self.assertEqual(mock_sheets_instance.mark_as_sent.call_count, 4)


if __name__ == "__main__":
    unittest.main()
