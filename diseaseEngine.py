import os
import json
import openai
from dotenv import load_dotenv
from diseaseHelperFunct import wait_for_run_completion, gpt_prompts, find_closest_medication

# Load your keys
load_dotenv()
client = openai.OpenAI()
openai.api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("ASSISTANT_ID") 
if not assistant_id:
    raise ValueError("Assistant ID is missing. Please check the .env file.")

provided_medications = None
oxygen_flag = None
diabetec_flag = None

def specialConditions(text2, o2_flag, diabetec_flag):
    """
    Inserts O₂ and Diabetes-related sentences into text2 at the correct location.
    """
    target_lines = (
        "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. "
        "SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit."
    )

    special_conditions_text = []
    if o2_flag:
        special_conditions_text.append("Check O₂ saturation level with signs and symptoms of respiratory distress.")
    if diabetec_flag:
        special_conditions_text.append(
            "SN to record blood sugar test results checked by Pt/PCG during the visits and report any significant changes to MD. "
            "SN to perform diabetic foot exam upon every visit. PCG assumes DM responsibilities, is confident, capable, and competent in checking blood sugar daily."
        )

    if special_conditions_text:
        conditions_text = " ".join(special_conditions_text)
        if target_lines in text2:
            text2 = text2.replace(target_lines, target_lines + " " + conditions_text, 1)
        else:
            text2 = conditions_text + " " + text2  # Fallback if target line is missing

    return text2

def check_for_keywords(response_json):
    show_button = False  # Default is False

    # Check if "no disease found" or "no medication found" is in the response text
    text1 = response_json.get("text1", "").lower()
    text2 = response_json.get("text2", "").lower()

    if "no disease found" in text1 or "no disease found" in text2:
        show_button = "1"  # No disease found, hide the button
    elif "no medication found" in text1 or "no medication found" in text2:
        show_button = "2"  # No medication found, hide the button
    else:
        show_button = "0"  # Otherwise, show the button

    return show_button




# Extract relevant data and split by '--', removing empty strings
def extract_and_split_diagnoses(extracted_data):
    # Extract the three diagnosis fields
    principal_diagnosis = extracted_data.get("patientDetails", {}).get("principalDiagnosis", "").strip()
    pertinent_diagnosis = extracted_data.get("patientDetails", {}).get("pertinentdiagnosis", "").strip()
    pertinent_diagnosis_cont = extracted_data.get("diagnosis", {}).get("pertinentdiagnosisCont", "").strip()
    

    # Combine them into a single list, excluding empty values
    combined_diagnoses = []
    
    if principal_diagnosis:
        combined_diagnoses.append(principal_diagnosis)
    if pertinent_diagnosis:
        combined_diagnoses.append(pertinent_diagnosis)
    if pertinent_diagnosis_cont:
        combined_diagnoses.append(pertinent_diagnosis_cont)
    
    # Split each diagnosis string by '--' and strip any extra spaces
    diseases_array = []
    for diagnosis in combined_diagnoses:
        diseases_array.extend([d.strip() for d in diagnosis.split("--") if d.strip()])


    return diseases_array
    

# 🛠 Main function
async def run_disease_processing(extracted_data):

    # get the disease array
    fullDiseasesArray = extract_and_split_diagnoses(extracted_data)
    diseasesArray = fullDiseasesArray[:9]

    global provided_medications
    global oxygen_flag
    global diabetec_flag


    # get the medication liat 
    provided_medications = extracted_data.get("medications", {}).get("medications", "").split("--")
    provided_medications = [m.strip() for m in provided_medications if m.strip()]

    # set the oxugen booleans
    oxygen_flag = extracted_data.get("diagnosis", {}).get("oxygen", False)
    diabetec_flag = extracted_data.get("diagnosis", {}).get("diabetec", False)


    print("check 1")
    mainContResponse = {}
    disease_mapping = {}

    for i, disease_name in enumerate(diseasesArray):
        if provided_medications:
            response =  wait_for_run_completion(client, assistant_id, disease_name, provided_medications, oxygen_flag, diabetec_flag)
            

        response_json = json.loads(response) if isinstance(response, str) else response
        response_json["showButton"] = check_for_keywords(response_json)
        if (response_json["showButton"] == "0"):
            response_json["text2"] = specialConditions(response_json["text2"], oxygen_flag, diabetec_flag)
        if (response_json["showButton"] == "2"):
            response_json["text1"] = "no medication found in database"
            response_json["text2"] = "no medication found in database"
            response_json["text1"] = "no medication found "

        print(f"in check 1: {i}")
        mainContResponse[f"page{i + 1}"] = response_json
        disease_mapping[f"page{i + 1}"] = disease_name
        
                # If provided medications are exhausted, generate a response for remaining diseases
        if not provided_medications:
            # Set dummy response for all remaining pages with no medications
            response_json["text1"] = "No medications left to process."
            response_json["text2"] = "No medications left to process."
            response_json["med"] ="No medications left to process."
            response_json["showButton"] = "3"  
        response_json["diseaseName"] = disease_name

        print(f"in check 2: {i}")
        # ✅ Remove used medication if found
        if "med" in response_json and response_json["med"] not in ["no medication found in database", ""]:
            used_medication = response_json["med"]
            closest_match = find_closest_medication(used_medication, provided_medications)
            if closest_match:
                provided_medications.remove(closest_match)

    print("final check 1")
    # ✅ Return result to frontend
    return {
        "mainContResponse": mainContResponse,
        "fullDiseasesArray": fullDiseasesArray
    }


# 🛠 Main function
async def run_differet_disease_processing(extracted_data, disease_name, diseaseNum = 9):

    global provided_medications
    global oxygen_flag
    global diabetec_flag



    # get the medication liat 
    provided_medications = extracted_data.get("medications", {}).get("medications", "").split("--")
    provided_medications = [m.strip() for m in provided_medications if m.strip()]

    # set the oxugen booleans
    oxygen_flag = extracted_data.get("diagnosis", {}).get("oxygen", False)
    diabetec_flag = extracted_data.get("diagnosis", {}).get("diabetec", False)

    # print(provided_medications, oxygen_flag, diabetec_flag)
    if provided_medications:
        response =  wait_for_run_completion(client, assistant_id, disease_name, provided_medications, oxygen_flag, diabetec_flag)
        

    response_json = json.loads(response) if isinstance(response, str) else response
    response_json["showButton"] = check_for_keywords(response_json)
    if (response_json["showButton"] == "0"):
        response_json["text2"] = specialConditions(response_json["text2"], oxygen_flag, diabetec_flag)
    
            # If provided medications are exhausted, generate a response for remaining diseases
    if not provided_medications:
        # Set dummy response for all remaining pages with no medications
        response_json["text1"] = "No medications left to process."
        response_json["text2"] = "No medications left to process."
        response_json["med"] ="No medications left to process."
        response_json["showButton"] = "3"  
    response_json["diseaseName"] = disease_name

    # ✅ Remove used medication if found
    if "med" in response_json and response_json["med"] not in ["no medication found in database", ""]:
        used_medication = response_json["med"]
        closest_match = find_closest_medication(used_medication, provided_medications)
        if closest_match:
            provided_medications.remove(closest_match)

    # print(response_json)
    # ✅ Return result to frontend
    # ✅ Return result to frontend
    return response_json



    
async def fetch_info_from_gpt2(query_type, query_value):

    global client
    global provided_medications
    global oxygen_flag
    global diabetec_flag

    gpt_prompt = gpt_prompts(query_type, query_value, provided_medications)

    print("check 1")
    gpt_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": gpt_prompt}]
    )

    gpt_result = gpt_response.choices[0].message.content.strip()
    print("check 2")
    # Extract JSON response
    json_start = gpt_result.find("{")
    json_end = gpt_result.rfind("}")

    json_response = gpt_result[json_start:json_end+1]  # Extract JSON content

    print("check 3")
    # Parse JSON
    parsed_response = json.loads(json_response)

    if query_type != "Medication":
        parsed_response["showButton"] = check_for_keywords(parsed_response)
        parsed_response["diseaseName"] = query_value

    if query_type == "Medication":
        parsed_response["med"] = "Medication left empty"
        parsed_response["showButton"] = "0"
        parsed_response["diseaseName"] = query_value

    print("check 4")
    return parsed_response




    