from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException, Form  
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import json
from extraction import main  
from diseaseEngine import run_initial_disease_processing , run_differet_disease_processing, fetch_info_from_gpt2
from fastapi.responses import StreamingResponse
from io import BytesIO
import zipfile
from wordFilling.wordFilling import fillDoc
from mangum import Mangum
import uuid

# for testing only
from dummy_data import get_extracted_data_storage, get_mainContResponse, get_diseaseList

session_store = {} 
# extracted_data_storage = None
# mainContResponse = None
# medicationList = None
# lastDiseaseNum = 10
# diseaseList = None
# totalDiseasePresent = None


# submission_data = {
#     "action": None,
#     "sn_name": None,
#     "appointment_dates": None,
#     "appointment_times": None,
#     "extraction_results": None,
# }

app = FastAPI(debug=True)
handler = Mangum(app)

# Allow frontend requests (from React app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can specify "http://localhost:3000" later)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy user credentials (you can later move to database)
VALID_USERNAME = "a"
VALID_PASSWORD = "a"

class LoginRequest(BaseModel):
    username: str
    password: str


def update_main_response(page_index, updated_data):
    global mainContResponse
    page_key = f"page{page_index + 1}"
    if page_key in mainContResponse:
        mainContResponse[page_key].update(updated_data)

@app.get("/")
def read_root():
    return {"message": "Backend is working!"}

# Login request
@app.post("/login")
def login(request: LoginRequest):

    if request.username == VALID_USERNAME and request.password == VALID_PASSWORD:
        # for testing only
        session_id = str(uuid.uuid4())
        session_store[session_id] = {
            "mainContResponse": None,
            "extracted_data_storage": None,
            "medicationList": None,
            "lastDiseaseNum": 9,
            "diseaseList": None,
            "totalDiseasePresent": None,
            "submission_data": {
                "action": None,
                "sn_name": None,
                "appointment_dates": None,
                "appointment_times": None,
                "extraction_results": None,
            }
        }
        return {"message": "Login successful", "session_id": session_id }

    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")


# extraction process
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), action: str = Form(...), sn_name: str = Form(...), appointment_dates: str = Form(...), appointment_times: str = Form(...), session_id: str = Form(...)  ):

    
    # global extracted_data_storage 
    # global submission_data
    try:
        session = session_store.get(session_id)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")
    
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        print("1")
        # Run your full processing function
        extracted_data = main(tmp_path)
        session["extracted_data_storage"] = extracted_data  

        print("2")

        # Extract the form data (appointment dates and times)
        appointment_dates = json.loads(appointment_dates)  # Convert the string to array
        appointment_times = json.loads(appointment_times)  # Convert the string to array
        print("3")

        print("🧪 extracted_data type:", type(session["extracted_data_storage"]))
        print("🧪 extracted_data content:", session["extracted_data_storage"])
        # In the future, you would run your extraction logic here
        session["submission_data"] = {
            "action": action,
            "sn_name": sn_name,
            "appointment_dates": appointment_dates,
            "appointment_times": appointment_times,
            "extraction_results": session["extracted_data_storage"],
        }
        print("4")
        # print(submission_data['action'])



        # return extracted_data  # ✅ Send full cleaned result
        return session["extracted_data_storage"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/save-extracted-data")
async def save_extracted_data(data: dict):
    try:
        session_id = data.get("session_id")
        modified_data = data.get("modified_data")

        session = session_store.get(session_id)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")

        session["extracted_data_storage"] = modified_data
        session["submission_data"]["extraction_results"] = modified_data

        return {"message": "Extracted data saved successfully", "data": modified_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving extracted data: {e}")



# disease ai process
@app.post("/disease-processing/")
async def run_disease_processing_endpoint(data: dict):
    session_id = data.get("session_id")
    session = session_store.get(session_id)
    print(f"Session ID: {session_id}")
    print(f"Session Data: {session}")
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    try:
        if session.get("extracted_data_storage") is None:
            raise HTTPException(status_code=400, detail="No extracted data available")

        # if mainContResponse == None:

        # Await the result of the disease processing function
        response_gpt = await run_initial_disease_processing(session.get("extracted_data_storage"), session)
        session["diseaseList"] = response_gpt['fullDiseasesArray']
        session["mainContResponse"] = response_gpt["mainContResponse"]
        session["totalDiseasePresent"] = len(session["diseaseList"]) - 1

        # totalDiseasePresent = len(diseaseList)
        print(f"disease list: {session["diseaseList"]}")
        print(f"disease list: {session["totalDiseasePresent"]}")        
        # mainContResponse = response_gpt['mainContResponse']

        return session.get("mainContResponse")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-main-cont-response/")
async def get_main_cont_response(session_id: str):
    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        mainContResponse = session.get("mainContResponse")
        if not mainContResponse:
            raise HTTPException(status_code=400, detail="No processed data available")

        return {"mainContResponse": mainContResponse}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/save-disease-data")
async def save_disease_data(data: dict):
    session_id = data.get("session_id")
    page_index = data.get("pageIndex")
    updated_data = data.get("updatedData")

    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        if page_index is None or page_index > 10:
            raise HTTPException(status_code=400, detail="Invalid page index")

        page_key = f"page{page_index + 1}"
        mainContResponse = session.get("mainContResponse", {})

        if page_key not in mainContResponse:
            raise HTTPException(status_code=404, detail="Page not found")

        mainContResponse[page_key].update(updated_data)
        return {"message": "Data saved successfully", "updated_data": updated_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run-different-disease")
async def run_different_disease(data: dict):
    session_id = data.get("session_id")
    page_index = data.get("index")

    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        lastDiseaseNum = session.get("lastDiseaseNum", 0)
        totalDiseasePresent = session.get("totalDiseasePresent", 0)
        diseaseList = session.get("diseaseList", [])

        if lastDiseaseNum > totalDiseasePresent:
            updated_disease_data = {
                "text1": "No more disease left to process",
                "text2": "No more disease left to process",
                "med": "No more disease left to process",
                "showButton": "1"
            }
        else:
            disease_name = diseaseList[lastDiseaseNum]
            extracted_data_storage = session.get("extracted_data_storage")
            updated_disease_data = await run_differet_disease_processing(session, disease_name)
            session["lastDiseaseNum"] = lastDiseaseNum + 1

        session["mainContResponse"][f"page{page_index + 1}"].update(updated_disease_data)

        return {"updated_data": updated_disease_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

  
    
@app.post("/run-same-disease-gpt")
async def run_same_disease_gpt(data: dict):
    try:
        session_id = data.get("session_id")
        session = session_store.get(session_id)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")

        disease_info = data.get("disease_info")
        original_info = data.get("original_info")
        updated_info = data.get("updated_info")

        print(f"🧾 Page Index: {data.get('index')}")
        print("Original Disease Name:", original_info.get("diseaseName"))
        print("Updated Disease Name:", updated_info.get("diseaseName"))
        print("Original Medication:", original_info.get("med"))
        print("Updated Medication:", updated_info.get("med"))

        original_disease = original_info.get("diseaseName", "").strip().lower()
        original_med = original_info.get("med", "").strip().lower()
        updated_disease = updated_info.get("diseaseName", "").strip().lower()
        updated_med = updated_info.get("med", "").strip().lower()

        if original_disease == updated_disease and original_med == updated_med:
            change_case = "Case 1: No changes"
            query_type = "Disease"
            disease_name = original_disease
            updated_disease_data = await run_differet_disease_processing(session, disease_name)

        elif original_disease != updated_disease and original_med != updated_med:
            change_case = "Case 2: Both disease and medication changed"
            query_type = "Custom-Disease-And-Med"
            disease_name = updated_disease
            updated_disease_data = await run_differet_disease_processing(session, disease_name, query_type, updated_med)

        elif original_disease != updated_disease and original_med == updated_med:
            change_case = "Case 3: Only disease changed"
            query_type = "Disease"
            disease_name = disease_info['diseaseName']
            updated_disease_data = await fetch_info_from_gpt2(query_type, disease_name, session)

        elif original_disease == updated_disease and original_med != updated_med:
            change_case = "Case 4: Only medication changed"
            query_type = "Custom-Medication"
            disease_name = disease_info['diseaseName']
            updated_disease_data = await run_differet_disease_processing(session, disease_name, query_type, updated_med)

        else:
            change_case = "Unknown case"
            updated_disease_data = {}

        print("🧪 Change Analysis:", change_case)

        session["mainContResponse"][f"page{data.get('index') + 1}"].update(updated_disease_data)
        return {"updated_data": updated_disease_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.post("/run-different-disease-gpt")
async def run_different_disease_gpt(data: dict):
    try:
        session_id = data.get("session_id")
        session = session_store.get(session_id)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")

        lastDiseaseNum = session.get("lastDiseaseNum", 0)
        totalDiseasePresent = session.get("totalDiseasePresent", 0)
        diseaseList = session.get("diseaseList", [])

        if lastDiseaseNum > totalDiseasePresent:
            updated_disease_data = {
                "text1": "No more disease left to process",
                "text2": "No more disease left to process",
                "med": "No more disease left to process",
                "showButton": "1"
            }
        else:
            disease_name = diseaseList[lastDiseaseNum]
            query_type = "Disease"
            updated_disease_data = await fetch_info_from_gpt2(query_type, disease_name, session)
            session["lastDiseaseNum"] = lastDiseaseNum + 1

        session["mainContResponse"][f"page{data.get('index') + 1}"].update(updated_disease_data)
        return {"updated_data": updated_disease_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/run-gpt-with-med")
async def run_gpt_with_med(data: dict):
    try:
        session_id = data.get("session_id")
        session = session_store.get(session_id)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")

        disease_info = data.get("disease_info")
        disease_name = disease_info['diseaseName']
        query_type = "Medication-filled"

        updated_disease_data = await fetch_info_from_gpt2(query_type, disease_name, session)
        session["mainContResponse"][f"page{data.get('index') + 1}"].update(updated_disease_data)

        return {"updated_data": updated_disease_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/run-gpt-without-med")
async def run_gpt_without_med(data: dict):
    try:
        session_id = data.get("session_id")
        session = session_store.get(session_id)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")

        disease_info = data.get("disease_info")
        disease_name = disease_info['diseaseName']
        query_type = "Medication-empty"

        updated_disease_data = await fetch_info_from_gpt2(query_type, disease_name, session)
        session["mainContResponse"][f"page{data.get('index') + 1}"].update(updated_disease_data)

        return {"updated_data": updated_disease_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/skip-page")
async def skip_page(data: dict):
    try:
        session_id = data.get("session_id")
        session = session_store.get(session_id)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")

        updated_data = {
            "text1": "Page Skipped",
            "text2": "Page Skipped",
            "med": "Page Skipped",
            "showButton": "4"
        }

        page_index = data.get("index")
        page_key = f"page{page_index + 1}"

        if page_key in session["mainContResponse"]:
            session["mainContResponse"][page_key].update(updated_data)

        return {"updated_data": updated_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-documents")
async def generate_documents(data: dict):
    try:
        session_id = data.get("session_id")
        session = session_store.get(session_id)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")

        submission_data = session.get("submission_data")
        mainContResponse = session.get("mainContResponse")

        if not submission_data or not mainContResponse:
            raise HTTPException(status_code=400, detail="Missing data for document generation.")
        # ✅ Only delete page10 if present
        if "page10" in mainContResponse:
            del mainContResponse["page10"]

        print("1")
        print("session_id", session_id)
        print("submission_data:", submission_data)
        print("mainContResponse keys:", list(mainContResponse.keys()))
        selectedDiseaseList = [page_data["diseaseName"] for page_data in mainContResponse.values()]
        print("selectedDiseaseList :", list(selectedDiseaseList))

        output_files = fillDoc(submission_data, mainContResponse, selectedDiseaseList)
        print("2")

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in output_files:
                zipf.writestr(file['filename'], file['file_buffer'].getvalue())

        print("3")
        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=documents.zip"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating documents: {str(e)}")
    

@app.get("/get-zip-filename")
async def get_zip_filename(session_id: str):
    try:
        session = session_store.get(session_id)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")

        name = session["extracted_data_storage"]['patientDetails']["name"]
        return {"filename": f"{name}.zip"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching filename: {str(e)}")