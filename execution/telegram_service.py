import os
import telebot
import requests
import io
import re
from urllib.parse import unquote
from pdf2image import convert_from_bytes


class TelegramService:
    def __init__(self):
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID")

        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
        if not self.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID environment variable is not set")

        self.bot = telebot.TeleBot(self.token)

    def _download_file(self, url: str) -> io.BytesIO:
        """Download a file from a URL, handling Google Drive and size limits."""
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            return None

        try:
            session = requests.Session()
            # Set a generic user agent
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })
            
            response = session.get(url, stream=True, timeout=60)

            # Handle Google Drive large file warning
            if "drive.google.com" in url:
                confirm = None
                for key, value in response.cookies.items():
                    if key.startswith("download_warning"):
                        confirm = value
                        break
                
                if confirm:
                    response = session.get(url, params={"confirm": confirm}, stream=True, timeout=60)

            response.raise_for_status()
            
            data = response.content
            
            # Basic check: if we got HTML but expected a file
            content_type = response.headers.get("Content-Type", "")
            if "text/html" in content_type and len(data) < 50000: # Small HTML is likely an error/warning page
                print(f"Warning: Downloaded content for {url} appears to be HTML ({content_type}).")

            file_io = io.BytesIO(data)
            
            # Extract filename more robustly
            filename = "file"
            content_disposition = response.headers.get("Content-Disposition", "")
            
            # Try filename* (modern standard, handles UTF-8)
            filename_utf8_match = re.search(r"filename\*=UTF-8''(.+)", content_disposition, re.IGNORECASE)
            if filename_utf8_match:
                filename = unquote(filename_utf8_match.group(1))
            else:
                # Try standard filename
                filename_match = re.search(r'filename="?([^";]+)"?', content_disposition, re.IGNORECASE)
                if filename_match:
                    filename = filename_match.group(1)
                    # Some servers send UTF-8 in filename= but don't encode it properly for headers
                    # We try to decode it if it looks like it's been mangled (Latin-1 to UTF-8)
                    try:
                        filename = filename.encode('iso-8859-1').decode('utf-8')
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        pass
                else:
                    filename = url.split("/")[-1].split("?")[0] or "file"
            
            # Ensure filename has an extension
            file_io.name = filename
            return file_io
        except Exception as e:
            print(f"Error downloading file {url}: {e}")
            return None

    def _generate_pdf_thumbnail(self, pdf_bytes: bytes) -> io.BytesIO:
        """Generate a thumbnail image from the first page of a PDF."""
        try:
            print("Generating thumbnail for PDF...")
            # Convert first page to image
            images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, size=(400, None))
            if images:
                thumb_io = io.BytesIO()
                images[0].save(thumb_io, format="JPEG", quality=85)
                thumb_io.seek(0)
                thumb_io.name = "thumbnail.jpg"
                return thumb_io
        except Exception as e:
            print(f"Failed to generate PDF thumbnail: {e}")
        return None

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
        Send a photo. Downloads it first if it's a URL.
        """
        try:
            sanitized_caption = self.sanitize_markdown(caption) if caption else None
            file_content = self._download_file(photo_url)
            
            if file_content:
                self.bot.send_photo(
                    self.chat_id,
                    file_content,
                    caption=sanitized_caption,
                    parse_mode="MarkdownV2" if sanitized_caption else None,
                )
            else:
                # Fallback to URL if download failed or it's not a URL
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
        Send a video. Downloads it first if it's a URL.
        """
        try:
            sanitized_caption = self.sanitize_markdown(caption) if caption else None
            file_content = self._download_file(video_url)
            
            if file_content:
                self.bot.send_video(
                    self.chat_id,
                    file_content,
                    caption=sanitized_caption,
                    parse_mode="MarkdownV2" if sanitized_caption else None,
                )
            else:
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

    def send_audio(self, audio_url: str, caption: str = None):
        """
        Send an audio file. Downloads it first if it's a URL.
        """
        try:
            sanitized_caption = self.sanitize_markdown(caption) if caption else None
            file_content = self._download_file(audio_url)
            
            if file_content:
                self.bot.send_audio(
                    self.chat_id,
                    file_content,
                    caption=sanitized_caption,
                    parse_mode="MarkdownV2" if sanitized_caption else None,
                )
            else:
                self.bot.send_audio(
                    self.chat_id,
                    audio_url,
                    caption=sanitized_caption,
                    parse_mode="MarkdownV2" if sanitized_caption else None,
                )
            print(f"Audio sent to {self.chat_id}: {audio_url}")
        except Exception as e:
            print(f"Failed to send audio: {e}")
            raise

    def send_document(self, document_url: str, caption: str = None):
        """
        Send a document. Downloads it first if it's a URL and generates a thumbnail for PDFs.
        """
        try:
            sanitized_caption = self.sanitize_markdown(caption) if caption else None
            file_content = self._download_file(document_url)
            
            if file_content:
                data = file_content.getvalue()
                thumbnail = None
                
                # If it's a PDF, try to generate a thumbnail
                if file_content.name.lower().endswith(".pdf"):
                    thumbnail = self._generate_pdf_thumbnail(data)
                
                # Reset pointer for the document itself
                file_content.seek(0)
                
                self.bot.send_document(
                    self.chat_id,
                    file_content,
                    thumbnail=thumbnail,
                    caption=sanitized_caption,
                    parse_mode="MarkdownV2" if sanitized_caption else None,
                )
            else:
                self.bot.send_document(
                    self.chat_id,
                    document_url,
                    caption=sanitized_caption,
                    parse_mode="MarkdownV2" if sanitized_caption else None,
                )
            print(f"Document sent to {self.chat_id}: {document_url}")
        except Exception as e:
            print(f"Failed to send document: {e}")
            raise
