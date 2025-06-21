import re
from fuzzywuzzy import process

def specialConditions(text2, o2_flag, diabetec_flag):
    """
    Inserts O₂ and Diabetes-related sentences after the third sentence of text2.
    """
    # Build the extra text
    special = []
    if o2_flag:
        special.append(
            "Check O₂ saturation level with signs and symptoms of respiratory distress."
        )
    if diabetec_flag:
        special.append(
            "SN to record blood sugar test results checked by Pt/PCG during the visits and report any significant changes to MD. "
            "SN to perform diabetic foot exam upon every visit. PCG assumes DM responsibilities, is confident, capable, and competent in checking blood sugar daily."
        )
    if not special:
        return text2  # Nothing to insert

    insert_text = " ".join(special)

    # Split into sentences (keeping the trailing period)
    sentences = re.split(r'(?<=[.])\s+', text2.strip())

    # If there are at least 3 sentences, insert after the third
    if len(sentences) >= 3:
        sentences.insert(3, insert_text)
        return " ".join(sentences)

    # Fallback: prepend if fewer than 3 sentences
    return insert_text + " " + text2


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


# Function to remove duplicates and normalize diagnoses using fuzzy matching
def get_unique_diseases(diseases_array, threshold=90):
    unique_diseases = []
    seen_diseases = []  # Keep track of diseases we've already seen (normalized)
    
    for disease in diseases_array:
        # Normalize: Remove any ICD code (assumes ICD code format is alpha-numeric, separated by space or commas)
        normalized_disease = re.sub(r'\s*\(.*\)\s*', '', disease)  # Remove anything in parentheses (e.g., ICD codes)
        normalized_disease = normalized_disease.strip().lower()  # Normalize case and strip spaces
        
        # Use fuzzy matching to compare the disease with already seen diseases
        closest_match = find_closest_disease(normalized_disease, seen_diseases, threshold)
        
        if closest_match is None:  # If no close match is found, consider it a unique disease
            unique_diseases.append(disease)
            seen_diseases.append(normalized_disease)  # Add to seen list

    return unique_diseases

# Fuzzy matching function to find the closest matching disease
def find_closest_disease(disease_name, seen_diseases, threshold=90):
    """
    Finds the closest matching disease name in the seen_diseases list using fuzzy matching.
    If a match is found above the threshold, return it; otherwise, return None.
    """
    if not seen_diseases:
        return None  # No diseases to compare against
    
    best_match, score = process.extractOne(disease_name, seen_diseases)
    
    return best_match if score >= threshold else None  

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

    unique_diseases = get_unique_diseases(diseases_array)


    return unique_diseases
    