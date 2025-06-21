import os
import json
import openai
from dotenv import load_dotenv
from diseaseHelperFunct import wait_for_run_completion, gpt_prompts, find_closest_medication
import re
from utilities import specialConditions, extract_and_split_diagnoses, check_for_keywords

# Load your keys
load_dotenv()
client = openai.OpenAI()
openai.api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("ASSISTANT_ID") 
assistant_id_2 = os.getenv("ASSISTANT_ID_2") 

if not assistant_id:
    raise ValueError("Assistant ID is missing. Please check the .env file.")


# 🛠 Main function
async def run_initial_disease_processing(extracted_data, session):

    # get the disease array
    fullDiseasesArray = extract_and_split_diagnoses(extracted_data)
    diseasesArray = fullDiseasesArray[:9]

    session["provided_medications"] = extracted_data.get("medications", {}).get("medications", "").split("--")
    session["provided_medications"] = [m.strip() for m in session["provided_medications"] if m.strip()]

    session["oxygen_flag"] = extracted_data.get("diagnosis", {}).get("oxygen", False)
    session["diabetec_flag"] = extracted_data.get("diagnosis", {}).get("diabetec", False)


    print("check 1")
    mainContResponse = {}
    disease_mapping = {}

    for i, disease_name in enumerate(diseasesArray):
        if session["provided_medications"]:
            response =  wait_for_run_completion(client, assistant_id, disease_name, session["provided_medications"])
            print("RAW GPT RESPONSE:", repr(response))
            raw = response  

            # strip any leading/trailing ```json fences
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.IGNORECASE)

            # now parse strictly
            response_json = json.loads(raw)
            response_json["showButton"] = check_for_keywords(response_json)
            if (response_json["showButton"] == "0"):
                # add oxygen and diabetc statements in initial run
                response_json["text2"] = specialConditions(response_json["text2"], session["oxygen_flag"], session["diabetec_flag"])
            if (response_json["showButton"] == "2"):
                response_json["text1"] = "no medication found in database"
                response_json["text2"] = "no medication found in database"
                response_json["med"] = "no medication found in database"

            print(f"in check 1: {i}")
            mainContResponse[f"page{i + 1}"] = response_json
            disease_mapping[f"page{i + 1}"] = disease_name
        
                # If provided medications are exhausted, generate a response for remaining diseases
        if not session["provided_medications"]:
            # Set dummy response for all remaining pages with no medications
            response_json["text1"] = "No medications left to process. Please select option to leave the place empty"
            response_json["text2"] = "No medications left to process. Please select option to leave the place empty"
            response_json["med"] ="No medications left to process. Please select option to leave the place empty"
            response_json["showButton"] = "2"  
        response_json["diseaseName"] = disease_name

        print(f"in check 2: {i}")

        print(response_json)
        # ✅ Remove used medication if found
        if "med" in response_json and response_json["med"] not in ["no medication found in database", ""]:
            used_medication = response_json["med"]
            closest_match = find_closest_medication(used_medication, session["provided_medications"])
            if closest_match:
                session["provided_medications"].remove(closest_match)

    print("final check 1")
    # ✅ Return result to frontend
    return {
        "mainContResponse": mainContResponse,
        "fullDiseasesArray": fullDiseasesArray
    }


# 🛠 run different dosease
async def run_differet_disease_processing(session, disease_name, query_type = None, updated_med = None):

    print(query_type, updated_med)
    print("1")
    if query_type == None and updated_med == None:
        # get the medication liat 
        print("diff disease")
        # provided_medications = extracted_data.get("medications", {}).get("medications", "").split("--")
        # provided_medications = [m.strip() for m in provided_medications if m.strip()]
        if session["provided_medications"]:
            response =  wait_for_run_completion(client, assistant_id, disease_name, session["provided_medications"])
        if not session["provided_medications"]:
            # Set dummy response for all remaining pages with no medications
            response_json["text1"] = "No medications left to process. Please select option to leave the place empty"
            response_json["text2"] = "No medications left to process. Please select option to leave the place empty"
            response_json["med"] ="No medications left to process. Please select option to leave the place empty"
            response_json["showButton"] = "2"  
    else:
        print("custom med")
        print(disease_name, updated_med)
        response =  wait_for_run_completion(client, assistant_id_2, disease_name, updated_med)
    print("2")
    # set the oxugen booleans
    # oxygen_flag = extracted_data.get("diagnosis", {}).get("oxygen", False)
    # diabetec_flag = extracted_data.get("diagnosis", {}).get("diabetec", False)

    print("RAW GPT RESPONSE:", repr(response))

    raw = response  # the assistant’s text

    # strip any leading/trailing ```json fences
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.IGNORECASE)
    response_json = json.loads(raw)

    response_json["showButton"] = check_for_keywords(response_json)
    if (response_json["showButton"] == "0"):
        response_json["text2"] = specialConditions(response_json["text2"], session["oxygen_flag"], session["diabetec_flag"])
    print("3") 
    if query_type == None and updated_med == None:
    # If provided medications are exhausted, generate a response for remaining diseases
        if not session["provided_medications"]:
            # Set dummy response for all remaining pages with no medications
            response_json["text1"] ="No medications left to process. Please select option to leave the place empty"
            response_json["text2"] = "No medications left to process. Please select option to leave the place empty"
            response_json["med"] ="No medications left to process. Please select option to leave the place empty"
            response_json["showButton"] = "2"  
            # ✅ Remove used medication if found
            if "med" in response_json and response_json["med"] not in ["no medication found in database", ""]:
                used_medication = response_json["med"]
                closest_match = find_closest_medication(used_medication, session["provided_medications"])
                if closest_match:
                    session["provided_medications"].remove(closest_match)
    else:
        response_json["showButton"] = "0"  

    response_json["diseaseName"] = disease_name



    # print(response_json)

    return response_json



async def fetch_info_from_gpt2(query_type, query_value, session):

    global client



    gpt_prompt = gpt_prompts(query_type, query_value, session["provided_medications"])

    gpt_response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "system", "content": gpt_prompt}]
)

    gpt_result = gpt_response.choices[0].message.content.strip()
    # Extract JSON response
    json_start = gpt_result.find("{")
    json_end = gpt_result.rfind("}")

    json_response = gpt_result[json_start:json_end+1]  # Extract JSON content

    # Parse JSON
    parsed_response = json.loads(json_response)

    if query_type != "Medication-empty":
        parsed_response["showButton"] = check_for_keywords(parsed_response)
        parsed_response["diseaseName"] = query_value
        

    if query_type == "Medication-empty":
        parsed_response["med"] = "Medication left empty"
        parsed_response["showButton"] = "0"
        parsed_response["diseaseName"] = query_value

    # no disease found in database of gpt
    if parsed_response["text2"] != "no medication found for the disease" or parsed_response["text2"] != "no disease found in database":
        parsed_response["text2"] = specialConditions(parsed_response["text2"], session["oxygen_flag"], session["diabetec_flag"])        

    print("check 4")
    return parsed_response




    