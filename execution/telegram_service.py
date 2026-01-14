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

    def sanitize_markdown(self, text: str) -> str:
        """Escape special characters for Telegram MarkdownV2."""
        if not text:
            return ""
        escape_chars = r"_*[]()~`>#+-=|{}.!"
        return "".join(f"\\{char}" if char in escape_chars else char for char in text)

    def send_message(self, message: str, parse_mode: str = None):
        """
        Send a message to the configured chat ID.

        Args:
            message: The message text to send
            parse_mode: Optional parse mode (e.g. 'MarkdownV2')
        """
        try:
            self.bot.send_message(self.chat_id, message, parse_mode=parse_mode)
            print(f"Message sent to {self.chat_id}: {message}")
        except Exception as e:
            print(f"Failed to send message: {e}")
            raise

    def send_photo(self, photo_url: str, caption: str = None):
        """
        Send a photo from a URL.

        Args:
            photo_url: The URL of the photo
            caption: Optional caption for the photo
        """
        try:
            sanitized_caption = self.sanitize_markdown(caption) if caption else None
            self.bot.send_photo(
                self.chat_id,
                photo_url,
                caption=sanitized_caption,
                parse_mode="MarkdownV2" if sanitized_caption else None,
            )
            print(f"Photo sent to {self.chat_id}: {photo_url}")
        except Exception as e:
            print(f"Failed to send photo: {e}")
            raise

    def send_video(self, video_url: str, caption: str = None):
        """
        Send a video from a URL.

        Args:
            video_url: The URL of the video
            caption: Optional caption for the video
        """
        try:
            sanitized_caption = self.sanitize_markdown(caption) if caption else None
            self.bot.send_video(
                self.chat_id,
                video_url,
                caption=sanitized_caption,
                parse_mode="MarkdownV2" if sanitized_caption else None,
            )
            print(f"Video sent to {self.chat_id}: {video_url}")
        except Exception as e:
            print(f"Failed to send video: {e}")
            raise

    def send_youtube(self, video_url: str, text: str = None):
        """
        Send a YouTube link with text, ensuring preview is enabled.

        Args:
            video_url: The YouTube video URL
            text: Optional text to accompany the link
        """
        try:
            sanitized_text = self.sanitize_markdown(text) if text else ""
            # In MarkdownV2, we can hide the URL in a zero-width space or just
            # append it. For simplicity and to ensure preview, we'll append
            # the URL. Telegram automatically generates previews for links.
            message = f"{sanitized_text}\n{video_url}" if sanitized_text else video_url

            self.bot.send_message(
                self.chat_id,
                message,
                parse_mode="MarkdownV2" if sanitized_text else None,
            )
            print(f"YouTube link sent to {self.chat_id}: {video_url}")
        except Exception as e:
            print(f"Failed to send YouTube link: {e}")
            raise
