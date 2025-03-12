import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Get credentials from .env file
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
RANGE_NAME = os.getenv("RANGE_NAME")

# Authenticate using Google Service Account
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
service = build("sheets", "v4", credentials=credentials)

def test_push_data():
    """Test function to push data with date, timestamp, and two test columns."""
    try:
        sheet = service.spreadsheets()

        # Get current date and timestamp
        current_date = datetime.now().strftime("%d/%m/%y")  # DD/MM/YY
        current_time = datetime.now().strftime("%H:%M:%S")  # HH:MM:SS

        # Example data for other columns
        test_column_3 = "Test Data 3"
        test_column_4 = "Test Data 4"

        values = [[current_date, current_time, test_column_3, test_column_4]]  # Four separate columns
        body = {"values": values}

        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption="RAW",
            body=body,
        ).execute()

        print(f"✅ Data successfully appended: {result.get('updates').get('updatedCells')} cells updated.")
    except Exception as e:
        print(f"❌ Error pushing data: {e}")

if __name__ == "__main__":
    test_push_data()