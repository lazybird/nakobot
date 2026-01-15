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
            content = task["content"]
            row = task["row"]
            msg_type = task["type"]
            status_col = task["status_col"]

            print(f"Processing row {row} (Type: {msg_type})...")

            try:
                if msg_type in ["image", "photo"]:
                    telegram.send_photo(content)
                elif msg_type == "video":
                    telegram.send_video(content)
                elif msg_type == "youtube":
                    telegram.send_youtube(content)
                elif msg_type == "audio":
                    telegram.send_audio(content)
                elif msg_type in ["pdf", "document", "file"]:
                    telegram.send_document(content)
                else:
                    # Default to text
                    telegram.send_message(content)

                print(f"Marking row {row} as sent...")
                sheets.mark_as_sent(row, status_col)

            except Exception as e:
                print(f"Failed to process row {row}: {e}")
                # Continue to next task instead of crashing entirely

        print("All tasks processed.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
