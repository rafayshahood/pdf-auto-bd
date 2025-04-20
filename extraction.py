import sys
from dotenv import load_dotenv
from unstract.llmwhisperer import LLMWhispererClientV2
from unstract.llmwhisperer.client import LLMWhispererClientException
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from datetime import datetime
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
import json


load_dotenv() 
extractionResults = []  # global variable available throughout the notebook

def clean_medications(medications_str, pain_medications_str):
    # Split into lists
    meds_list = [m.strip() for m in medications_str.split('--') if m.strip()]
    pain_list = [p.strip() for p in pain_medications_str.split('--') if p.strip()]

    # Step 1: Check for Tylenol
    tylenol_in_meds = [m for m in meds_list if 'tylenol' in m.lower()]
    tylenol_in_pain = any('tylenol' in p.lower() for p in pain_list)

    # If Tylenol is in meds, move to painMedications if not already there
    if tylenol_in_meds:
        meds_list = [m for m in meds_list if 'tylenol' not in m.lower()]
        if not tylenol_in_pain:
            pain_list.append(tylenol_in_meds[0])

    # 🔁 Recalculate tylenol presence after modification
    tylenol_in_pain = any('tylenol' in p.lower() for p in pain_list)

    # Step 2: If Tylenol is not in either list
    if not tylenol_in_meds and not tylenol_in_pain:
        if len(pain_list) > 1:
            first = pain_list[0]
            extras = pain_list[1:]
            for med in extras:
                if not any(med.lower() in m2.lower() for m2 in meds_list):
                    meds_list.append(med)
            pain_list = [first]

    # Step 3: If Tylenol is in pain list and there are other items
    if tylenol_in_pain and len(pain_list) > 1:
        filtered_pain = []
        for med in pain_list:
            if 'tylenol' in med.lower():
                filtered_pain.append(med)
            else:
                if not any(med.lower() in m2.lower() for m2 in meds_list):
                    meds_list.append(med)
        pain_list = filtered_pain

    # Convert lists back to strings
    updated_medications = ' -- '.join(meds_list)
    updated_pain_medications = ' -- '.join(pain_list)

    return updated_medications, updated_pain_medications


def count_occurrences_of_flags(words_to_count,text):
    text_lower = text.lower()  # Convert text to lowercase for case-insensitive matching
    total_count = sum(text_lower.count(word) for word in words_to_count)
    return total_count

def getFlags(ex_txt, check_words, wordCount = 0):
    # Example usage:
    flag = False

    count = count_occurrences_of_flags(check_words, ex_txt)
    if count > wordCount:
        flag = True

    print(f"Total occurrences of {check_words}: {count}")

    return flag

class PatientDetails(BaseModel):
    # medical record no.
    medicalRecordNo: str = Field(description="Medical Record No. of the individual")
    # patient name
    # # patient name
    name: str = Field(description="What is the Patient's Name?")
    # # provider name
    providerName: datetime = Field(description="In section 7. Provider's Name, Address, and Telephone Number, what is the provider's name? Only take info from section 7. Provider's Name, Address, and Telephone Number while answering this question and do not take info from any other part of the extracted text")
    # principal diagnosis
    principalDiagnosis: str = Field(description="principal diagnosis of the patient?")
    # all other pertinant diagnosis
    pertinentdiagnosis: str = Field(description="Other Pertinant Diagnosis of the individual. This section contains disease e.g I11.9 Hypertensive heart disease with. I11.9 is code, do not include this in the output only the disease name e.g Hypertensive heart disease with Only include . Separate each disease with a --")

    
class Diagnosis(BaseModel):
    # all other pertinant diagnosis cont
    pertinentdiagnosisCont: str = Field(description="Other Pertinent Diagnoses continued. If not present return empty string. Separate each disease with a -")
    # constipation check
    constipated: bool = Field(description="in section MEDICAL SUMMARY / NECESSITY tell whether the patient is constipated or not")
    # pain areas
    painIn: str = Field(description="Pain in which places of the patien. If information is not present return empty string")
    # depression check
    # depression: bool = Field(description="In section 19. Mental Status, Whether the individual is depressed or not?")
    # diabetec
    diabetec: bool = Field(description="Does the patient suffer from Diabetes Mellitus Type 2?")
    # oxygen val
    oxygen: bool = Field(description="In section 21. Orders for Discipline and Treatments continued. Under the heading: SN TO PERFORM EVERY VISIT, check whether a statment containing the text inside the following brackets [Check o2 saturation level with signs] is present or not.?")
    
class Medications(BaseModel):
    # all medications
    medications: str = Field(description="10. Medications: Dose/Frequency/Route (N)ew (C)hanged.  Separate each medication with a --")
    painMedications: str = Field(description="What is the pain medication give to the individual? Copy paste the pain medication with instruction. If there is no pain medication return empty string. If pain medication is not present return empty strin")

class ExtraDetails(BaseModel):
    # safety measures
    safetyMeasures: str = Field(description="Copy Paste 15. Safety Measures and 15. Safety Measures continued  from page 1, 2,3 and 4 only. Do not take any from other pages, do not add anything from your own.Separate Each with ,")
    # safetyMeasures: str = Field(description="15. Safety Measures")
    # safety measures
    # safetyMeasuresCont: str = Field(description="15. Safety Measures continued")
    #  all nurtitional requirements
    nutritionalReq: str = Field(description="16. Nutritional Requirements")
    #  all nurtitional cont requirements
    nutritionalReqCont: str = Field(description="16. Nutrition Req. continued. If it is not present return empty string")
    # edema info
    edema: str = Field(description="Edema Management") 
    # cane walker check
    # can: bool = Field(description="Whether the individual has cane in 18.B. Activites Permitted?")
    # walker: bool = Field(description="Whether the individual has walker in 18.B. Activites Permitted?")

    

class Form485(BaseModel):
    patientDetails: PatientDetails = Field(description="Personal details of the patient")
    diagnosis: Diagnosis = Field(description="Diagnosis of the patient")
    medications: Medications = Field(description="Mediactions of the patient")
    extraDetails: ExtraDetails = Field(description="Extra Details of the patient")

def error_exit(error_message):
    print(error_message)
    sys.exit(1)



def process_485_information(extracted_text):
    preamble = ("What you are seeing is a filled out Home health Health Certification and Plan of care form. Your job is to extract the information from it accurately.")
    postamble = "Do not include any explanation in the reply. Do not change any information extracted from the form. Only include the extracted information in the reply."
    system_template = "{preamble}"
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_template = "{format_instructions}\n\n{extracted_text}\n\n{postamble}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    parser = PydanticOutputParser(pydantic_object=Form485)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    request = chat_prompt.format_prompt(preamble=preamble,
                                        format_instructions=parser.get_format_instructions(),
                                        extracted_text=extracted_text,
                                        postamble=postamble).to_messages()
    chat = ChatOpenAI(model="gpt-4o-mini")  # Use GPT-4 here
    response = chat(request, temperature=0.0)
    # print(f"Response from LLM:\n{response.content}")
    return response.content


def extract_text_from_pdf(file_path, pages_list=None):
    llmw = LLMWhispererClientV2()

    
    try:
        result = llmw.whisper(
            file_path=file_path, 
            wait_for_completion=True,
            wait_timeout=200,
            output_mode = 'layout_preserving',
            mode = 'form',
            
        )        
        extracted_text = result["extraction"]['result_text']
        return extracted_text
    except LLMWhispererClientException as e:
        error_exit(e)


def process_485_pdf(file_path, pages_list=None):
    global extractionResults  # Declare that we're modifying the global variable
    extracted_text = extract_text_from_pdf(file_path, pages_list)
    # print(extracted_text)
    response = process_485_information(extracted_text)
    extractionResults = response  

    # If extractionResults is already a dict, you can use it directly.
    if isinstance(extractionResults, dict):
        extractionResults = extractionResults

    else:
        # Remove markdown formatting if present
        json_string = extractionResults
        if json_string.startswith("```json"):
            json_string = json_string.replace("```json", "").replace("```", "").strip()
        try:
            extractionResults = json.loads(json_string)
        except json.JSONDecodeError as e:
            error_exit(f"Error decoding JSON: {e}")

    extractionResults['diagnosis']['depression'] = getFlags(extracted_text, ["depressed", "depression"],1)
    extractionResults['extraDetails']['vertigo'] = getFlags(extracted_text, ["Vertigo", "vertigo"], 0)
    extractionResults['extraDetails']['palpitation'] = getFlags(extracted_text, ["palpitation", "Palpitation", "palpitations,","Palpitations"], 1)
    # Extract safety measures (handling case sensitivity)
    safety_measures = extractionResults["extraDetails"].get("safetyMeasures", "").lower()

    # Set flags based on presence
    extractionResults["extraDetails"]["can"] = "true" if "cane" in safety_measures else "false"
    extractionResults["extraDetails"]["walker"] = "true" if "walker" in safety_measures else "false"

    extractionResults["medications"]["medications"], extractionResults["medications"]["painMedications"] = clean_medications(extractionResults["medications"]["medications"], extractionResults["medications"]["painMedications"])



    print(f"Response from LLM:\n{extractionResults}")
    # print(extractionResults)
    
    return extractionResults




def main(filepath):
    load_dotenv()
    result = process_485_pdf(filepath, "1")
    return result
    


if __name__ == "__main__":
    main()
