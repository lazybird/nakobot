import os
import base64
import json
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def check_sheet_status():
    encoded_creds = os.environ.get("GREETS_SERVICE_ACCOUNT_JSON")
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    
    decoded_creds = base64.b64decode(encoded_creds).decode("utf-8")
    creds_dict = json.loads(decoded_creds)
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1
    
    rows = sheet.get_all_values()
    header = [h.lower() for h in rows[0]]
    data_rows = rows[1:]
    
    date_col_idx = next(i for i, h in enumerate(header) if "date" in h)
    status_col_idx = next(i for i, h in enumerate(header) if "statut" in h)
    content_col_idx = next(i for i, h in enumerate(header) if "message" in h or "contenu" in h)
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_fr = datetime.now().strftime("%d/%m/%Y")
    
    print(f"Checking tasks for today ({today} / {today_fr})...")
    
    found_any = False
    for i, row in enumerate(data_rows):
        date_str = row[date_col_idx]
        status = row[status_col_idx]
        content = row[content_col_idx]
        
        if date_str == today or date_str == today_fr:
            found_any = True
            print(f"Row {i+2}: '{content[:30]}...' | Status: {status}")
            
    if not found_any:
        print("No tasks found for today.")

if __name__ == "__main__":
    check_sheet_status()
