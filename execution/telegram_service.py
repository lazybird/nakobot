import os
import telebot

class TelegramService:
    def __init__(self):
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
        if not self.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID environment variable is not set")

        self.bot = telebot.TeleBot(self.token)

    def send_message(self, message: str):
        """Send a message to the configured chat ID."""
        try:
            self.bot.send_message(self.chat_id, message)
            print(f"Message sent to {self.chat_id}: {message}")
        except Exception as e:
            print(f"Failed to send message: {e}")
            raise
