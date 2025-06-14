import time
import json
import logging
from dotenv import load_dotenv
from fuzzywuzzy import process  # Import fuzzy string matching
import os
import openai
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("ASSISTANT_ID") 


def find_closest_medication(med_name, med_list, threshold=75):
    """
    Finds the closest matching medication name in the provided medication list using fuzzy matching.
    If a match is found above the threshold, return it; otherwise, return None.
    """
    if not med_list:
        return None  # No available medications to match

    best_match, score = process.extractOne(med_name.lower(), med_list)
    
    return best_match if score >= threshold else None  # Only return if similarity is high

# Function that sends the request and waits for completion
def wait_for_run_completion(client, assistant_id, disease_name, provided_medications, sleep_interval=5):
    try:
        # print(f"disease_name : {disease_name}")
        # print(f"provided_medications : {provided_medications}")
        # Create a new thread for each request
        empty_thread = client.beta.threads.create()
        thread_id = empty_thread.id

        print(f"thread_id : {thread_id}")
        print(f"assistant_id : {assistant_id}")


       # Prepare the message with flags and medication list
        message_with_flags = f"Disease Name: {disease_name}\nMedicationList: {list(provided_medications)}"
        # print(f"message_with_flags : {message_with_flags}")
        # Send the request to the assistant
        client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=message_with_flags
        )

        # Start the assistant run
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        message_with_flags
        # print(f"run : {run}")
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if run.completed_at:
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value

                # Delete the thread after retrieving the response
                client.beta.threads.delete(thread_id)
                return response

            logging.info("Waiting for run to complete...")
            time.sleep(sleep_interval)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None



        


def gpt_prompts(query_type, query_value, medication_list = None):
  if query_type == "Disease":
    gpt_prompt = f"""
    You are a highly structured medical assistant.

    TASK: Search for structured medical information on the disease: '{query_value}'. 
    - Ignore any leading code in the disease name (e.g., "I11.9 Hypertensive heart disease" → "Hypertensive heart disease").
    - Try to select a medication for the disease from the following provided list:
    {medication_list}
    - If a matching medication is found, use it exactly as provided (including dosage and instructions). DO NOT modify or reformat it.
    - - If no matching medication is found, return "no medication found" in all responses (text1, text2, med fields).
    - Ensure text1, text2, and med fields remain synchronized.
    - Escape all double quotes (") inside text fields to prevent JSON errors.

    
    RESPONSE FORMAT (STRICTLY FOLLOW THIS JSON FORMAT):
    {{
        "text1": "Altered status due to {query_value}. Knowledge deficit regarding measures to control {query_value} and the medication [find a medication with instructions e.g Janumet 50-1000 mg, 1 tablet by mouth 2 times daily] as ordered by MD.",
        "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. [150-200 words description of disease]. .SN instructed Patient/PCG regarding the medication [medication name e.g Janumet 50-1000 mg].  [30-50 word description of medication]. SN advised Patient/PCG to take medication [medication with instructions e.g Janumet 50-1000 mg, 1 tablet by mouth 2 times daily] as ordered by MD.",
        "med": "[medication name exactly as selected]"
    }}

    [] is a placeolder that needs to be replaced by the desired information as mentioned inside each brackets.

    
    STRICT GUIDELINES:
    - If matching medication found in the provided list, use the exact text without changes.
    - Always fill the "med" field with the medication name.
    - If no matching medication found from the list return:
        {{
        "text1": "no medication found for the disease",
        "text2": "no medication found for the disease",
        "med": "no medication found for the disease"
    }}
    - If the disease is not found, return:
    {{
        "text1": "no disease found in database",
        "text2": "no disease found in database",
        "med": "no disease found in database"
    }}
    - Always return ONLY valid JSON (no extra text, no commentary).
    - Escape all double quotes (") properly inside text fields.
    - Follow the specified format exactly—do not alter structure or wording.
    """
 
  elif query_type == "Medication-filled" :  
            gpt_prompt = f"""
        You are a highly structured medical assistant.

        TASK: Search for structured medical information on the disease: '{query_value}'.
        - If the disease name contains a leading code (e.g., "I11.9 Hypertensive heart disease with"), **ignore the code** and use only the disease name.
        - FIRST try to select a medication for the disease from the following provided list:
        {medication_list}
        - If a matching medication is found, use it exactly as provided (including dosage and instructions). DO NOT modify or reformat it.
        - If no matching medication is found, return "no medication found" in all responses (text1, text2, med fields).
        - Ensure `text1`, `text2`, and `med` fields remain synchronized.
        - Escape all double quotes (") inside text fields to prevent JSON errors.

        RESPONSE FORMAT (STRICTLY FOLLOW THIS JSON FORMAT):
        {{
            "text1": "Altered status due to {query_value}. Knowledge deficit regarding measures to control {query_value} and the medication [find a medication with instructions e.g Janumet 50-1000 mg, 1 tablet by mouth 2 times daily] as ordered by MD.",
            "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues, and psychosocial adjustment. [150-200 words description of disease]. SN instructed Patient/PCG regarding the medication [medication name e.g Janumet 50-1000 mg]. [30-50 word description of medication]. SN advised Patient/PCG to take medication [medication with instructions e.g Janumet 50-1000 mg, 1 tablet by mouth 2 times daily] as ordered by MD.",
            "med": "[medication name exactly as selected]"
        }}

        STRICT GUIDELINES:
        - If a medication is found, use the exact text without changes.
        - If no matching medication found from the list return:
                {{
                "text1": "no medication found for the disease",
                "text2": "no medication found for the disease",
                "med": "no medication found for the disease"
            }}
        - Always return ONLY valid JSON (no extra text, no commentary).
        - Escape all double quotes (") properly inside text fields.
        - Follow the specified format exactly—do not alter structure or wording.
        - If the disease is not found, return:
        {{
            "text1": "no disease found in database",
            "text2": "no disease found in database",
            "med": "no disease found in database"
        }}
        """


  elif query_type == "Medication-empty" :  

    gpt_prompt = f"""
        You are a highly structured medical assistant.

        TASK: Search for structured medical information on the disease: '{query_value}'. 
        - If the disease name contains a leading code (e.g., "I11.9 Hypertensive heart disease with"), **ignore the code** and use only the disease name.
        - **Escape all double quotes (`"`) inside text fields** to ensure JSON validity.
        - Ensure `text1` and `text2` remain synchronized.

        RESPONSE FORMAT (STRICTLY FOLLOW THIS JSON FORMAT):
        {{
            "text1": "Altered status due to {query_value}. Knowledge deficit regarding measures to control {query_value} and the medication //???medication info and usage???// as ordered by MD.",
            "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. [150-200 words description of disease]. .SN instructed Patient/PCG regarding the medication //???medication name???//.  //??medication description 30-50 words???//. SN advised Patient/PCG to take medication //???medication info and usage???// as ordered by MD."
        }}
        
        STRICT GUIDELINES:
        - **Return ONLY valid JSON** (no extra text or formatting outside JSON).
        - **Escape all double quotes (`"`) inside text fields** to prevent JSON parsing errors.  
        - **Follow the specified format exactly—do not alter structure or wording.
        - **Exclude unnecessary information (e.g., sources, extra text).
        - **Exclude unnecessary information (e.g., sources, extra text).
        
        - **If the disease is not found, return:**
            {{
            "text1": "no disease found in database",
            "text2": "no disease found in database"
            }}
        """
    
  else:
      gpt_prompt = "None"
  
  return gpt_prompt
