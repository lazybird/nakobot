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
- **Smart Send**: If the message starts with `http`, the bot automatically tries to detect if it's an image, video, PDF, or a simple link (handling Google Drive and YouTube automatically).

## Configuration

The bot uses the following environment variables in a `.env` file:

- `TELEGRAM_BOT_TOKEN`: The API token for your bot (from @BotFather).
- `TELEGRAM_CHAT_ID`: The ID of the group or channel where messages will be sent.
- `TELEGRAM_MESSAGE_THREAD_ID` (Optional): The ID of the specific topic (thread) within a group.
- `GOOGLE_SHEET_ID`: The ID of the Google Sheet containing the schedule.
- `GREETS_SERVICE_ACCOUNT_JSON`: Base64 encoded service account credentials.

### How to find IDs

#### Finding the Chat ID
1. Add the bot `@raw_data_bot` to your group. It will immediately output a JSON containing the `id` of the chat (starts with `-100` for supergroups).
2. Alternatively, use the browser: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` after sending a message to the group.

#### Finding the Topic ID (Message Thread ID)
1. **Using Message Link**: Right-click a message in the target topic and select "Copy Message Link". The link will look like `https://t.me/c/123456789/45/67`. The middle number (**45**) is the Topic ID.
2. **Using Telegram Web**: When clicking on a topic, the URL will end with something like `_45`.
3. **Using @raw_data_bot**: Add the bot to the group and send a message *inside* the desired topic. Look for `message_thread_id` in the output.

