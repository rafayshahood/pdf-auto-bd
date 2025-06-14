import requests
import random
import json
from pathlib import Path
from datetime import datetime, timedelta
from time import sleep
from tqdm import tqdm

# === CONFIGURATION ===
API_URL = "http://localhost:8000"
PDF_FOLDER = Path("./test_pdfs")
RESULTS_FOLDER = Path("./results")
DOWNLOAD_FOLDER = Path("./downloads")
RESULTS_FOLDER.mkdir(exist_ok=True)
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

USERNAME = "a"
PASSWORD = "a"

RETRY_OPTIONS = [
    ("run-same-disease-gpt", "Same disease retry"),
    ("run-different-disease", "Try different disease"),
    ("run-gpt-with-med", "Retry with medication"),
    ("run-gpt-without-med", "Retry without medication")
]

def generate_dates(n):
    base_date = datetime.today()
    return [(base_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(n)]

def generate_times(n):
    base_time = datetime.strptime("10:00", "%H:%M")
    return [(base_time + timedelta(minutes=30 * i)).strftime("%H:%M") for i in range(n)]

def login():
    res = requests.post(f"{API_URL}/login", json={"username": USERNAME, "password": PASSWORD})
    res.raise_for_status()
    print("✅ Logged in")

def upload_pdf(pdf_path, sn_name, action, dates, times, save_dir):
    with open(pdf_path, "rb") as f:
        files = {"file": f}
        data = {
            "sn_name": sn_name,
            "action": action,
            "appointment_dates": json.dumps(dates),
            "appointment_times": json.dumps(times)
        }
        print(f"📤 Uploading: {pdf_path.name}")
        res = requests.post(f"{API_URL}/upload/", files=files, data=data)
        res.raise_for_status()
        extraction = res.json()
        with open(save_dir / "extraction.json", "w") as out:
            json.dump(extraction, out, indent=2)
        return extraction

def run_disease_processing(save_dir):
    print("🧠 Running GPT disease processing...")
    res = requests.post(f"{API_URL}/disease-processing/")
    for _ in tqdm(range(20), desc="⌛ Waiting for GPT"):
        sleep(3)
    res.raise_for_status()
    full_response = res.json()
    result = full_response.get("result") or full_response  # Fix: extract list
    with open(save_dir / "disease_processing.json", "w") as out:
        json.dump(result, out, indent=2)
    return result

def handle_gpt_retries(gpt_result, save_dir):
    for i, page in enumerate(gpt_result):
        # Skip retry logic — just save result as-is
        retry_file = save_dir / f"no_retry_page_{i+1}.json"
        with open(retry_file, "w") as out:
            json.dump({
                "note": "No retry triggered — continuing with original GPT result",
                "original_result": page
            }, out, indent=2)
        print(f"🔄 Page {i+1}: No retry — saved original result.")

def generate_zip():
    print("📦 Generating ZIP...")
    res = requests.post(f"{API_URL}/generate-documents")
    res.raise_for_status()
    return res

def get_zip_filename():
    res = requests.get(f"{API_URL}/get-zip-filename")
    res.raise_for_status()
    return res.json()["filename"]

def save_zip(content, filename):
    path = DOWNLOAD_FOLDER / filename
    with open(path, "wb") as f:
        f.write(content)
    print(f"✅ ZIP saved: {path}")

def main():
    login()
    pdf_files = list(PDF_FOLDER.glob("*.pdf"))
    if not pdf_files:
        print("❌ No PDF files found in ./test_pdfs/")
        return

    for i, pdf in enumerate(pdf_files):
        print(f"\n=== Processing {pdf.name} ===")
        action = random.choice(["Reset", "Discharge"])
        count = 9 if action == "Reset" else 10
        dates = generate_dates(count)
        times = generate_times(count)
        sn_name = f"Test SN {i+1}"

        base_name = pdf.stem.replace(" ", "_")
        save_dir = RESULTS_FOLDER / base_name
        save_dir.mkdir(exist_ok=True)

        upload_pdf(pdf, sn_name, action, dates, times, save_dir)
        gpt_result = run_disease_processing(save_dir)
        handle_gpt_retries(gpt_result, save_dir)
        zip_response = generate_zip()
        filename = get_zip_filename()
        save_zip(zip_response.content, filename)

if __name__ == "__main__":
    main()