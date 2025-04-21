from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException, Form  
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import json
from extraction import main  
from diseaseEngine import run_disease_processing , run_differet_disease_processing, fetch_info_from_gpt2
from fastapi.responses import StreamingResponse
from io import BytesIO
import zipfile
from wordFilling.wordFilling import fillDoc



extracted_data_storage = None
mainContResponse = None
medicationList = None
lastDiseaseNum = 9
diseaseList = None

submission_data = {
    "action": None,
    "sn_name": None,
    "appointment_dates": None,
    "appointment_times": None,
    "extraction_results": None,
}

app = FastAPI()

# Configure CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, can restrict later
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

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


@app.get("/")
def read_root():
    return {"message": "Backend is working!"}

# Login request
@app.post("/login")
def login(request: LoginRequest):
    global mainContResponse, extracted_data_storage, medicationList, diseaseNum
    mainContResponse = None
    extracted_data_storage = None
    medicationList = None
    diseaseNum = None
    
    global submission_data
    submission_data = {
    "action": None,
    "sn_name": None,
    "appointment_dates": None,
    "appointment_times": None,
    "extraction_results": None,
    }


    if request.username == VALID_USERNAME and request.password == VALID_PASSWORD:
        return {"message": "Login successful"}

    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")


# extraction process
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), action: str = Form(...), sn_name: str = Form(...), appointment_dates: str = Form(...), appointment_times: str = Form(...)):
    global extracted_data_storage 
    global submission_data

    file_size = len(await file.read())  # Get the file size
    
    try:


        # Read the file content once
        file_content = await file.read()

        # Check file size
        file_size = len(file_content)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size is too large. Maximum allowed size is {MAX_FILE_SIZE // (1024 * 1024)} MB.",
            )
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Store dummy extracted data in the backend
        # extracted_data_storage = {
        #     "patientDetails": {
        #         "medicalRecordNo": "000000156-001",
        #         "name": "FORD, HENRY",
        #         "providerName": "MINT Home Health Care Inc.",
        #         "principalDiagnosis": "Primary osteoarthritis, left shoulder",
        #         "pertinentdiagnosis": "Primary osteoarthritis, right -- Spondylosis w/o myelopathy or radiculopathy -- Essential (primary) hypertension -- Unspecified asthma, uncomplicated -- Edema, unspecified -- Weakness -- Iron deficiency anemia, unspecified -- Hyperlipidemia, unspecified -- Vitamin D deficiency, unspecified -- History of falling"
        #     },
        #     "diagnosis": {
        #         "pertinentdiagnosisCont": "",
        #         "constipated": False,
        #         "painIn": "Lower Back, Bilateral Shoulders, Joints",
        #         "diabetec": False,
        #         "oxygen": True,
        #         "depression": False
        #     },
        #     "medications": {
        #         "medications": "Chlorthalidone 25 mg, 1 tablet by mouth daily -- Rosuvastatin 10 mg, 1 tablet by mouth daily -- Magnesium 250 mg, 1 tablet by mouth daily -- Albuterol HFA 90 mcg, inhale 2 puffs by mouth 2 times daily -- Aspirin 81 mg, 1 tablet by mouth daily -- Ibuprofen 600 mg, 1 tablet by mouth every 6 hours as needed for pain -- Pain Reliever Ointment Gel, apply topically to affected area 2 times daily -- Ferrous Sulfate 325 mg, 1 tablet by mouth daily -- Vitamin D3 2000 International Units, 1 capsule by mouth daily -- Oyster Shell Calcium 500 mg, 1 tablet by mouth daily",
        #         "painMedications": "Tylenol 500 mg, 1 capsule by mouth every 6 hours as needed for pain"
        #     },
        #     "extraDetails": {
        #         "safetyMeasures": "Bleeding precautions, Fall precautions, Clear pathways, Infection control -- Walker, Cane, Universal Precautions, 911 protocol, COVID-19 Precautions",
        #         "nutritionalReq": "NAS, Low fat, Low cholesterol",
        #         "nutritionalReqCont": "",
        #         "edema": "Pedal R/L, Pitting +1",
        #         "vertigo": False,
        #         "palpitation": False,
        #         "can": "true",
        #         "walker": "true"
        #     }
        # }

        # Run your full processing function
        extracted_data = main(tmp_path)
        extracted_data_storage = extracted_data  


        # Extract the form data (appointment dates and times)
        appointment_dates = json.loads(appointment_dates)  # Convert the string to array
        appointment_times = json.loads(appointment_times)  # Convert the string to array

        # In the future, you would run your extraction logic here
        submission_data = {
            "action": action,
            "sn_name": sn_name,
            "appointment_dates": appointment_dates,
            "appointment_times": appointment_times,
            "extraction_results": extracted_data_storage,
        }

        # print(submission_data['action'])



        # return extracted_data  # ✅ Send full cleaned result
        return extracted_data_storage

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/save-extracted-data")
async def save_extracted_data(modified_data: dict):
    try:
        global extracted_data_storage 
        extracted_data_storage = modified_data  
        submission_data['extraction_results'] = extracted_data_storage

        return {"message": "Extracted data saved successfully", "data": extracted_data_storage}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving extracted data: {e}")



# disease ai process
@app.post("/disease-processing/")
async def run_disease_processing_endpoint():
    try:
        if extracted_data_storage is None:
            raise HTTPException(status_code=400, detail="No extracted data available")
        
        global mainContResponse
        global diseaseList
        
        # if mainContResponse == None:

        # Await the result of the disease processing function
        response_gpt = await run_disease_processing(extracted_data_storage)
        diseaseList = response_gpt['fullDiseasesArray']
        mainContResponse = response_gpt['mainContResponse']

        # print(mainContResponse)
        # print(diseaseList)

        # diseaseList = ['Primary osteoarthritis, left shoulder', 'Primary osteoarthritis, right', 'Spondylosis w/o myelopathy or radiculopathy', 'Essential (primary) hypertension', 'Unspecified asthma, uncomplicated', 'Edema, unspecified', 'Weakness', 'Iron deficiency anemia, unspecified', 'Hyperlipidemia, unspecified', 'Vitamin D deficiency, unspecified', 'History of falling']

            # Send the processed data to frontend
            # return relevant_data  # Return the result from disease processing

        # mainContResponse = {
        #         "page1": {
        #             "text1": "Altered status due to Primary osteoarthritis, left shoulder. Knowledge deficit regarding measures to control Primary osteoarthritis, left shoulder and the medication Ibuprofen 600 mg, 1 tablet by mouth every 6 hours as needed for pain as ordered by MD.",
        #             "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Primary osteoarthritis of the shoulder is a gradual wearing of the articular cartilage that leads to pain and stiffness. As the joint surface degenerates, the subchondral bone remodels, losing its sphericity and congruity. The joint capsule also becomes thickened, leading to further loss of shoulder rotation. Osteoarthritis most often occurs in people who are over age 50. In younger people, it can result from an injury or trauma. SN instructed Patient/PCG regarding the medication Ibuprofen 600 mg. It is used to relieve pain from various conditions and reduces pain, swelling, and joint stiffness caused by arthritis. SN advised Patient/PCG to take medication Ibuprofen 600 mg, 1 tablet by mouth every 6 hours as needed for pain as ordered by MD.",
        #             "med": "Ibuprofen 600 mg, 1 tablet by mouth every 6 hours as needed for pain",
        #             "showButton": "1" ,
        #             "diseaseName": "Fever"
        #         },
        #         "page2": {
        #             "text1": "Altered status due to Primary osteoarthritis. Knowledge deficit regarding measures to control Primary osteoarthritis and the medication Pain Reliever Ointment Gel, apply topically to affected area 2 times daily as ordered by MD.",
        #             "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Primary osteoarthritis is mostly related to aging. With aging, the water content of the cartilage increases and the protein makeup of cartilage degenerates. Repetitive use of joints over the years causes damage to the cartilage that leads to joint pain and swelling. Arm pain, depending on the location and cause, may be accompanied by numbness, redness, swelling, tenderness, or stiffness of the joints. The goal of treatment in osteoarthritis is to reduce joint pain and inflammation while improving and maintaining joint function. SN instructed Patient/PCG regarding the medication Pain Reliever Ointment Gel. This topical medication is used to relieve pain in the affected joints by applying it directly to the skin. SN advised Patient/PCG to apply Pain Reliever Ointment Gel, apply topically to affected area 2 times daily as ordered by MD.",
        #             "med": "Pain Reliever Ointment Gel, apply topically to affected area 2 times daily",
        #             "showButton": "2" ,
        #             "diseaseName": "Flue"
        #         },
        #         "page3": {
        #             "text1": "Altered status due to Spondylosis w/o myelopathy or radiculopathy. Knowledge deficit regarding measures to control Spondylosis w/o myelopathy or radiculopathy and the medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
        #             "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Spondylosis w/o myelopathy or radiculopathy is an age-related change of the bones (vertebrae) and discs of the spine. These changes are often called degenerative disc disease and osteoarthritis. These changes don't always cause symptoms. But they are a common cause of spine problems that can range from mild to severe. Spondylosis w/o myelopathy or radiculopathy lumbar region refers to disease involving the lumbar spinal nerve root. This can manifest as pain, numbness, or weakness of the buttock and leg. SN instructed Patient/PCG regarding the medication Rosuvastatin 10 mg. Rosuvastatin is used along with a proper diet to help lower \"bad\" cholesterol and fats in the blood. SN advised Patient/PCG to take medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
        #             "med": "Rosuvastatin 10 mg, 1 tablet by mouth daily",
        #             "showButton": "3" ,
        #             "diseaseName": "Cold"
        #         },
        #         "page4": {
        #             "text1": "Altered status due to Spondylosis w/o myelopathy or radiculopathy. Knowledge deficit regarding measures to control Spondylosis w/o myelopathy or radiculopathy and the medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
        #             "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Spondylosis w/o myelopathy or radiculopathy is an age-related change of the bones (vertebrae) and discs of the spine. These changes are often called degenerative disc disease and osteoarthritis. These changes don't always cause symptoms. But they are a common cause of spine problems that can range from mild to severe. Spondylosis w/o myelopathy or radiculopathy lumbar region refers to disease involving the lumbar spinal nerve root. This can manifest as pain, numbness, or weakness of the buttock and leg. SN instructed Patient/PCG regarding the medication Rosuvastatin 10 mg. Rosuvastatin is used along with a proper diet to help lower \"bad\" cholesterol and fats in the blood. SN advised Patient/PCG to take medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
        #             "med": "Rosuvastatin 10 mg, 1 tablet by mouth daily",
        #             "showButton": "4" ,
        #             "diseaseName": "Injury"
        #         },
        #         "page5": {
        #             "text1": "Altered status due to Primary osteoarthritis, left shoulder. Knowledge deficit regarding measures to control Primary osteoarthritis, left shoulder and the medication Ibuprofen 600 mg, 1 tablet by mouth every 6 hours as needed for pain as ordered by MD.",
        #             "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Primary osteoarthritis of the shoulder is a gradual wearing of the articular cartilage that leads to pain and stiffness. As the joint surface degenerates, the subchondral bone remodels, losing its sphericity and congruity. The joint capsule also becomes thickened, leading to further loss of shoulder rotation. Osteoarthritis most often occurs in people who are over age 50. In younger people, it can result from an injury or trauma. SN instructed Patient/PCG regarding the medication Ibuprofen 600 mg. It is used to relieve pain from various conditions and reduces pain, swelling, and joint stiffness caused by arthritis. SN advised Patient/PCG to take medication Ibuprofen 600 mg, 1 tablet by mouth every 6 hours as needed for pain as ordered by MD.",
        #             "med": "Ibuprofen 600 mg, 1 tablet by mouth every 6 hours as needed for pain",
        #             "showButton": "1" ,
        #             "diseaseName": "Muscle Pain"
        #         },
        #         "page6": {
        #             "text1": "Altered status due to Primary osteoarthritis. Knowledge deficit regarding measures to control Primary osteoarthritis and the medication Pain Reliever Ointment Gel, apply topically to affected area 2 times daily as ordered by MD.",
        #             "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Primary osteoarthritis is mostly related to aging. With aging, the water content of the cartilage increases and the protein makeup of cartilage degenerates. Repetitive use of joints over the years causes damage to the cartilage that leads to joint pain and swelling. Arm pain, depending on the location and cause, may be accompanied by numbness, redness, swelling, tenderness, or stiffness of the joints. The goal of treatment in osteoarthritis is to reduce joint pain and inflammation while improving and maintaining joint function. SN instructed Patient/PCG regarding the medication Pain Reliever Ointment Gel. This topical medication is used to relieve pain in the affected joints by applying it directly to the skin. SN advised Patient/PCG to apply Pain Reliever Ointment Gel, apply topically to affected area 2 times daily as ordered by MD.",
        #             "med": "Pain Reliever Ointment Gel, apply topically to affected area 2 times daily",
        #             "showButton": "2" ,
        #             "diseaseName": "Chemo"
        #         },
        #         "page7": {
        #             "text1": "Altered status due to Spondylosis w/o myelopathy or radiculopathy. Knowledge deficit regarding measures to control Spondylosis w/o myelopathy or radiculopathy and the medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
        #             "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Spondylosis w/o myelopathy or radiculopathy is an age-related change of the bones (vertebrae) and discs of the spine. These changes are often called degenerative disc disease and osteoarthritis. These changes don't always cause symptoms. But they are a common cause of spine problems that can range from mild to severe. Spondylosis w/o myelopathy or radiculopathy lumbar region refers to disease involving the lumbar spinal nerve root. This can manifest as pain, numbness, or weakness of the buttock and leg. SN instructed Patient/PCG regarding the medication Rosuvastatin 10 mg. Rosuvastatin is used along with a proper diet to help lower \"bad\" cholesterol and fats in the blood. SN advised Patient/PCG to take medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
        #             "med": "Rosuvastatin 10 mg, 1 tablet by mouth daily",
        #             "showButton": "3" ,
        #             "diseaseName": "Hepatites"
        #         },
        #         "page8": {
        #             "text1": "Altered status due to Spondylosis w/o myelopathy or radiculopathy. Knowledge deficit regarding measures to control Spondylosis w/o myelopathy or radiculopathy and the medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
        #             "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Spondylosis w/o myelopathy or radiculopathy is an age-related change of the bones (vertebrae) and discs of the spine. These changes are often called degenerative disc disease and osteoarthritis. These changes don't always cause symptoms. But they are a common cause of spine problems that can range from mild to severe. Spondylosis w/o myelopathy or radiculopathy lumbar region refers to disease involving the lumbar spinal nerve root. This can manifest as pain, numbness, or weakness of the buttock and leg. SN instructed Patient/PCG regarding the medication Rosuvastatin 10 mg. Rosuvastatin is used along with a proper diet to help lower \"bad\" cholesterol and fats in the blood. SN advised Patient/PCG to take medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
        #             "med": "Rosuvastatin 10 mg, 1 tablet by mouth daily",
        #             "showButton": "4" ,
        #             "diseaseName": "sweating"
        #         },
        #         "page9": {
        #             "text1": "Altered status due to Spondylosis w/o myelopathy or radiculopathy. Knowledge deficit regarding measures to control Spondylosis w/o myelopathy or radiculopathy and the medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
        #             "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Spondylosis w/o myelopathy or radiculopathy is an age-related change of the bones (vertebrae) and discs of the spine. These changes are often called degenerative disc disease and osteoarthritis. These changes don't always cause symptoms. But they are a common cause of spine problems that can range from mild to severe. Spondylosis w/o myelopathy or radiculopathy lumbar region refers to disease involving the lumbar spinal nerve root. This can manifest as pain, numbness, or weakness of the buttock and leg. SN instructed Patient/PCG regarding the medication Rosuvastatin 10 mg. Rosuvastatin is used along with a proper diet to help lower \"bad\" cholesterol and fats in the blood. SN advised Patient/PCG to take medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
        #             "med": "Rosuvastatin 10 mg, 1 tablet by mouth daily",
        #             "showButton": "4" ,
        #             "diseaseName": "laziness"
        #         }
        #     }
        


        return mainContResponse  # Return the dummy data for testing purposes

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-main-cont-response/")
async def get_main_cont_response():
    try:
        global mainContResponse

        # If mainContResponse is not set, return an error message
        if not mainContResponse:
            raise HTTPException(status_code=400, detail="No processed data available")

        return {
            "mainContResponse": mainContResponse
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/save-disease-data")
async def save_disease_data(data: dict):
    try:
        page_index = data.get("pageIndex")
        updated_data = data.get("updatedData")

        global mainContResponse

        # Check if the page index is valid
        if page_index is None or page_index > 10:
            raise HTTPException(status_code=400, detail="Invalid page index")

        page_key = f"page{page_index + 1}" 
        
        if page_key not in mainContResponse:
            raise HTTPException(status_code=404, detail="Page not found")

        mainContResponse[page_key].update(updated_data)

        return {"message": "Data saved successfully", "updated_data": updated_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run-different-disease")
async def run_different_disease(data: dict):
    try:
        # Process for running a different disease

        disease_info = data.get("disease_info")
        global lastDiseaseNum
        disease_name = diseaseList[lastDiseaseNum] 
        print(disease_name)
        updated_disease_data = await run_differet_disease_processing(extracted_data_storage, disease_name, lastDiseaseNum)
        lastDiseaseNum = lastDiseaseNum +1

        global mainContResponse
        page_index = data.get("index")
        pageNum = page_index+1
        pageToMatch = "page"+str(pageNum)
        # Save the updated data to the global storage 
        if page_index is not None and page_index < 10:
            for key in mainContResponse.keys():
                if key == pageToMatch:
                    mainContResponse[key].update(updated_disease_data)  # Update the specific page
            
        return {"updated_data": updated_disease_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/run-same-disease-gpt")
async def run_same_disease_gpt(data: dict):
    try:
        # Process for running a different disease
        disease_info = data.get("disease_info")

        print(disease_info)

        query_type = "Disease"
        disease_name = disease_info['diseaseName']
        
        updated_disease_data = await fetch_info_from_gpt2(query_type, disease_name)

        global mainContResponse
        # print(mainContResponse)
        page_index = data.get("index")
        pageNum = page_index+1
        pageToMatch = "page"+str(pageNum)

        # Save the updated data to the global storage (or database)
        if page_index is not None and page_index < 10:
            for key in mainContResponse.keys():
                if key == pageToMatch:
                    mainContResponse[key].update(updated_disease_data)  # Update the specific page
            

        return {"updated_data": updated_disease_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/run-different-disease-gpt")
async def run_different_disease_gpt(data: dict):
    try:
        # Process for running a different disease
        disease_info = data.get("disease_info")


        global lastDiseaseNum
        disease_name = diseaseList[lastDiseaseNum] 

        query_type = "Disease"
        updated_disease_data = await fetch_info_from_gpt2(query_type, disease_name)
        lastDiseaseNum = lastDiseaseNum +1

        global mainContResponse
        # print(mainContResponse)
        page_index = data.get("index")
        pageNum = page_index+1
        pageToMatch = "page"+str(pageNum)

        # Save the updated data to the global storage (or database)
        if page_index is not None and page_index < 10:
            for key in mainContResponse.keys():
                if key == pageToMatch:
                    mainContResponse[key].update(updated_disease_data)  # Update the specific page
            

        return {"updated_data": updated_disease_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/run-gpt-with-med")
async def run_gpt_with_med(data: dict):
    try:
        # Process for running a different disease
        disease_info = data.get("disease_info")

        global mainContResponse
        disease_name = disease_info['diseaseName']

        query_type = "Medication-filled"
        updated_disease_data = await fetch_info_from_gpt2(query_type, disease_name)

        page_index = data.get("index")
        pageNum = page_index+1
        pageToMatch = "page"+str(pageNum)

        # Save the updated data to the global storage (or database)
        if page_index is not None and page_index < 10:
            for key in mainContResponse.keys():
                if key == pageToMatch:
                    print(key)
                    mainContResponse[key].update(updated_disease_data)  # Update the specific page
            
        return {"updated_data": updated_disease_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/run-gpt-without-med")
async def run_gpt_without_med(data: dict):
    try:
        # Process for running a different disease
        disease_info = data.get("disease_info")

        global mainContResponse
        disease_name = disease_info['diseaseName']

        query_type = "Medication-empty"
        updated_disease_data = await fetch_info_from_gpt2(query_type, disease_name)

        page_index = data.get("index")
        pageNum = page_index+1
        pageToMatch = "page"+str(pageNum)

        # Save the updated data to the global storage (or database)
        if page_index is not None and page_index < 10:
            for key in mainContResponse.keys():
                if key == pageToMatch:
                    print(key)
                    mainContResponse[key].update(updated_disease_data)  # Update the specific page
            
        return {"updated_data": updated_disease_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/skip-page")
async def skip_page(data: dict):
    try:
        # Modify the page's content
        updated_data = {
            "text1": "Page Skipped",
            "text2": "Page Skipped",
            "med": "Page Skipped",
            "showButton": "4"
        }

        global mainContResponse
        # print(mainContResponse)
        page_index = data.get("index")
        pageNum = page_index+1
        pageToMatch = "page"+str(pageNum)
        # Save the updated data to the global storage (or database)
        if page_index is not None and page_index < 10:
            for key in mainContResponse.keys():
                if key == pageToMatch:
                    mainContResponse[key].update(updated_data)  # Update the specific page
            

        return {"updated_data": updated_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



# Generate documents and send as a streaming response
@app.post("/generate-documents")
async def generate_documents():
    try:
        global submission_data
        global mainContResponse

        # Generate the disease list
        selectedDiseaseList = [page_data["diseaseName"] for page_data in mainContResponse.values()]

        # Call fillDoc to generate documents
        output_files = fillDoc(submission_data, mainContResponse, selectedDiseaseList)

        # Create an in-memory ZIP file to send all documents
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in output_files:
                zipf.writestr(file['filename'], file['file_buffer'].getvalue())

        zip_buffer.seek(0)

        # Return the file as a streaming response
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=documents.zip"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating documents: {str(e)}")
    

# API to fetch the filename for the ZIP
@app.get("/get-zip-filename")
async def get_zip_filename():
    try:
        # Extract the filename from your data
        zip_name = extracted_data_storage['patientDetails']["name"]  # You can modify this logic as per your need
        
        # Return the filename
        return {"filename": f"{zip_name}.zip"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching filename: {str(e)}")
    

