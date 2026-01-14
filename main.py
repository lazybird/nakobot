from execution.telegram_service import TelegramService
from execution.sheets_service import SheetsService
import sys
from dotenv import load_dotenv

load_dotenv()


def main():
    print("Initializing Nakobot...")

    try:
        telegram = TelegramService()
        sheets = SheetsService()

        print("Checking for due tasks...")
        tasks = sheets.get_due_tasks()

        if not tasks:
            print("No tasks due for today.")
            return

        print(f"Found {len(tasks)} tasks.")

        for task in tasks:
            message = task["message"]
            row = task["row"]

            print(f"Processing row {row}: Sending message...")
            telegram.send_message(message)

            print(f"Marking row {row} as sent...")
            sheets.mark_as_sent(row)

        print("All tasks processed.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
