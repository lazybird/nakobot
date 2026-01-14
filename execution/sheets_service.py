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
        Returns a list of dicts with row index, message, and type.
        """
        rows = self.sheet.get_all_values()
        if not rows:
            return []

        header = [h.lower() for h in rows[0]]
        data_rows = rows[1:]

        # Dynamic column finding
        try:
            date_col_idx = next(i for i, h in enumerate(header) if "date" in h)
            status_col_idx = next(i for i, h in enumerate(header) if "statut" in h)
            # Support 'message' or 'contenu'
            content_col_idx = next(
                i for i, h in enumerate(header) if "message" in h or "contenu" in h
            )
        except StopIteration:
            print("Error: Required columns (Date, Statut, Message/Contenu) not found.")
            return []

        # Optional Type column
        try:
            type_col_idx = next(i for i, h in enumerate(header) if "type" in h)
        except StopIteration:
            type_col_idx = None

        due_tasks = []

        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")
        today_fr = datetime.now().strftime("%d/%m/%Y")

        for i, row in enumerate(data_rows):
            # Row index in sheet is i + 2 (1 for header, 1 for 0-index)
            row_idx = i + 2

            # SAFEGUARD: Ensure row has enough columns for required fields
            max_idx = max(date_col_idx, status_col_idx, content_col_idx)
            if len(row) <= max_idx:
                continue

            date_str = row[date_col_idx]
            content = row[content_col_idx]
            status = row[status_col_idx]

            task_type = "text"
            if type_col_idx is not None and len(row) > type_col_idx:
                val = row[type_col_idx].strip().lower()
                if val:
                    task_type = val

            # Check date (support ISO and FR formats)
            is_today = (date_str == today) or (date_str == today_fr)

            if is_today and status == "À envoyer":
                due_tasks.append(
                    {"row": row_idx, "content": content, "type": task_type}
                )

        return due_tasks

    def mark_as_sent(self, row_index):
        """Updates the status column (Col C, index 3) to 'Envoyé'."""
        self.sheet.update_cell(row_index, 3, "Envoyé")
