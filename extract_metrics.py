import os
import openai
import logging
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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Authenticate with OpenAI API
openai.api_key = OPENAI_API_KEY

# Authenticate with Google Sheets API
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
service = build("sheets", "v4", credentials=credentials)

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_metrics(transcription):
    """
    Uses OpenAI to extract 'Physical Win' and 'Social Highlight' from the transcription.
    Returns a dictionary with the extracted values.
    """
    prompt = (
        f"Analyze the following text and extract insights:\n\n"
        f"\"{transcription}\"\n\n"
        f"Identify the following two metrics:\n"
        f"1. **Physical Win**: A statement about any physical activity or movement.\n"
        f"2. **Social Highlight**: A statement about any social interaction or event.\n\n"
        f"If a metric is found, provide its exact statement. If not found, return 'None'.\n\n"
        f"Format your response as:\n"
        f"Physical Win: [value or 'None']\n"
        f"Social Highlight: [value or 'None']\n"
    )

    try:
        logging.debug(f"Sending request to OpenAI with text: {transcription}")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )

        output = response['choices'][0]['message']['content']
        logging.debug(f"Received OpenAI response: {output}")

        # Extract metrics from OpenAI response
        metrics = {}
        for metric in ["Physical Win", "Social Highlight"]:
            match = output.split(f"{metric}:")[-1].strip().split("\n")[0]
            metrics[metric] = match if match.lower() != "none" else None

        return metrics
    except Exception as e:
        logging.error(f"Error processing metrics: {e}")
        return {}

def append_to_google_sheet(transcription):
    """Extracts metrics and uploads data to Google Sheets."""
    extracted_metrics = extract_metrics(transcription)

    try:
        sheet = service.spreadsheets()

        # Get current date and timestamp
        current_date = datetime.now().strftime("%d/%m/%y")  # DD/MM/YY
        current_time = datetime.now().strftime("%H:%M:%S")  # HH:MM:SS

        # Prepare row data (only add non-empty values)
        row = [current_date, current_time] + [
            extracted_metrics.get("Physical Win", ""),
            extracted_metrics.get("Social Highlight", "")
        ]

        body = {"values": [row]}
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption="RAW",
            body=body,
        ).execute()

        print("✅ Data successfully appended.")
        return extracted_metrics
    except Exception as e:
        print(f"❌ Error pushing data to Google Sheets: {e}")