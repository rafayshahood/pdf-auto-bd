import re
from fuzzywuzzy import process

# Function to extract and split diagnoses
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
    
    # Call function to get unique diseases using fuzzy matching
    unique_diseases = get_unique_diseases(diseases_array)
    
    return unique_diseases

# Function to remove duplicates and normalize diagnoses using fuzzy matching
def get_unique_diseases(diseases_array, threshold=75):
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
def find_closest_disease(disease_name, seen_diseases, threshold=75):
    """
    Finds the closest matching disease name in the seen_diseases list using fuzzy matching.
    If a match is found above the threshold, return it; otherwise, return None.
    """
    if not seen_diseases:
        return None  # No diseases to compare against
    
    best_match, score = process.extractOne(disease_name, seen_diseases)
    
    return best_match if score >= threshold else None  # Only return if similarity is high enough

# Example usage with your data
extracted_data = {
    'patientDetails': {
        'medicalRecordNo': '000000167-001',
        'name': 'TYSON, MIKE',
        'providerName': 'MINT Home Health Care Inc.',
        'principalDiagnosis': 'Spondylosis w/o myelopathy or radiculopathy',
        'pertinentdiagnosis': 'Pain in right shoulder -- Bilateral primary osteoarthritis -- Hypertensive heart disease -- Major depressive disorder -- Other abnormalities of gait -- Mixed hyperlipidemia -- Generalized anxiety disorder -- Vitamin D deficiency -- Gastro-esophageal reflux disease without esophagitis -- Hypomagnesemia -- Age-related cognitive decline -- Personal history of TIA and cerebral infarction without residual deficits -- History of falling',
    },
    'diagnosis': {
        'pertinentdiagnosisCont': 'F41.1 Generalized anxiety disorder -- E55.9 Vitamin D deficiency, unspecified -- K21.9 Gastro-esophageal reflux disease without esophagitis -- E83.42 Hypomagnesemia -- R41.81 Age-related cognitive decline -- Z86.73 Personal history of TIA (TIA) and cerebral infarction without residual deficits -- Z91.81 History of falling',
    }
}

fullDiseasesArray = extract_and_split_diagnoses(extracted_data)
print(fullDiseasesArray)