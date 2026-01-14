from execution.telegram_service import TelegramService
import sys
from dotenv import load_dotenv

load_dotenv()


def main():
    print("Initializing Nakobot...")

    try:
        telegram = TelegramService()
        telegram.send_message("Hello")
        print("Test message sent successfully.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
