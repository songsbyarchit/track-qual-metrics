from flask import Flask, render_template, request
from extract_metrics import append_to_google_sheet

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    extracted_metrics = None
    message = ""

    if request.method == "POST":
        transcription = request.form.get("transcription")

        if transcription.strip():
            append_to_google_sheet(transcription)  # Process and store in Sheets
            extracted_metrics = append_to_google_sheet(transcription)  # Get extracted data
            message = "✅ Data successfully appended to Google Sheets!"

    return render_template("index.html", extracted_metrics=extracted_metrics, message=message)

if __name__ == "__main__":
    app.run(debug=True)