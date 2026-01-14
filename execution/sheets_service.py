import os
import base64
import json
import gspread
from google.oauth2.service_account import Credentials


class SheetsService:
    def __init__(self):
        encoded_creds = os.environ.get("GREETS_SERVICE_ACCOUNT_JSON")
        sheet_id = os.environ.get("GOOGLE_SHEET_ID")

        if not encoded_creds:
            raise ValueError(
                "GREETS_SERVICE_ACCOUNT_JSON environment variable is not set"
            )
        if not sheet_id:
            raise ValueError("GOOGLE_SHEET_ID environment variable is not set")

        decoded_creds = base64.b64decode(encoded_creds).decode("utf-8")
        creds_dict = json.loads(decoded_creds)

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(sheet_id).sheet1

    def get_due_tasks(self):
        """
        Retrieves all rows where:
        - Date d'envoi (Col A) == Today (YYYY-MM-DD or DD/MM/YYYY)
        - Statut (Col C) == 'À envoyer'
        Returns a list of dicts with row index and message.
        """
        all_records = self.sheet.get_all_records()
        # Note: gspread get_all_records returns a list of dicts.
        # We need to filter manually.
        # However, to update the status, we need the row number.
        # Using get_all_values might be safer to track row indices (1-based).

        rows = self.sheet.get_all_values()
        header = rows[0]  # Assuming first row is header: Date, Message, Statut
        data_rows = rows[1:]

        due_tasks = []

        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")
        today_fr = datetime.now().strftime("%d/%m/%Y")

        for i, row in enumerate(data_rows):
            # Row index in sheet is i + 2 (1 for header, 1 for 0-index)
            row_idx = i + 2

            # SAFEGUARD: Ensure row has enough columns
            if len(row) < 3:
                continue

            date_str = row[0]
            message = row[1]
            status = row[2]

            # Check date (support ISO and FR formats)
            is_today = (date_str == today) or (date_str == today_fr)

            if is_today and status == "À envoyer":
                due_tasks.append({"row": row_idx, "message": message})

        return due_tasks

    def mark_as_sent(self, row_index):
        """Updates the status column (Col C, index 3) to 'Envoyé'."""
        self.sheet.update_cell(row_index, 3, "Envoyé")
