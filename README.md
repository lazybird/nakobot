# Nakobot

Nakobot is a Telegram bot automated via Google Sheets. It reads scheduled messages from a Google Sheet and sends them to a configured Telegram chat.

## Supported Message Types

The bot supports the following message types, specified in the 'Type' column of the Google Sheet:

- **`text`** (default): Sends a standard text message. If the column is empty or contains an unrecognized type, it defaults to text.
- **`image`** or **`photo`**: Sends an image. The content must be a direct URL to the image file (e.g., ending in `.jpg`, `.png`).
- **`video`**: Sends a video file. The content must be a direct URL to the video file (e.g., ending in `.mp4`).
- **`youtube`**: Sends a YouTube video link. The bot ensures a preview is generated. The content should be the YouTube video URL.
- **`audio`**: Sends an audio file. The content must be a direct URL to the audio file (e.g., MP3).
- **`pdf`**, **`document`**, or **`file`**: Sends a general file (like a PDF). The content must be a direct URL to the file.
