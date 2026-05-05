import os
import telebot
import sys


def verify_chat_id():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    print(f"Testing Token: {token[:5]}...")
    print(f"Testing Chat ID: {chat_id}")

    if not token or not chat_id:
        print("Error: Token or Chat ID not set.")
        sys.exit(1)

    bot = telebot.TeleBot(token)

    try:
        sent_message = bot.send_message(
            chat_id, "Test message from Nakobot verification script to new ID."
        )
        print(
            f"Successfully sent message to {chat_id}. Message ID: {sent_message.message_id}"
        )
    except Exception as e:
        print(f"Failed to send message: {e}")
        sys.exit(1)


if __name__ == "__main__":
    verify_chat_id()
