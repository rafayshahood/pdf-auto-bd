# dummy_data.py
import copy
extracted_data_storage = {
    "patientDetails": {
        "medicalRecordNo": "000000156-001",
        "name": "FORD, HENRY",
        "providerName": "MINT Home Health Care Inc.",
        "principalDiagnosis": "Primary osteoarthritis, left shoulder",
        "pertinentdiagnosis": "Primary osteoarthritis, right -- Spondylosis w/o myelopathy or radiculopathy -- Essential (primary) hypertension -- Unspecified asthma, uncomplicated -- Edema, unspecified -- Weakness -- Iron deficiency anemia, unspecified -- Hyperlipidemia, unspecified -- Vitamin D deficiency, unspecified -- History of falling"
    },
    "diagnosis": {
        "pertinentdiagnosisCont": "",
        "constipated": False,
        "painIn": "Lower Back, Bilateral Shoulders, Joints",
        "diabetec": False,
        "oxygen": True,
        "depression": False
    },
    "medications": {
        "medications": "Chlorthalidone 25 mg, 1 tablet by mouth daily -- Rosuvastatin 10 mg, 1 tablet by mouth daily -- Magnesium 250 mg, 1 tablet by mouth daily -- Albuterol HFA 90 mcg, inhale 2 puffs by mouth 2 times daily -- Aspirin 81 mg, 1 tablet by mouth daily -- Ibuprofen 600 mg, 1 tablet by mouth every 6 hours as needed for pain -- Pain Reliever Ointment Gel, apply topically to affected area 2 times daily -- Ferrous Sulfate 325 mg, 1 tablet by mouth daily -- Vitamin D3 2000 International Units, 1 capsule by mouth daily -- Oyster Shell Calcium 500 mg, 1 tablet by mouth daily",
        "painMedications": "Tylenol 500 mg, 1 capsule by mouth every 6 hours as needed for pain"
    },
    "extraDetails": {
        "safetyMeasures": "Bleeding precautions, Fall precautions, Clear pathways, Infection control -- Walker, Cane, Universal Precautions, 911 protocol, COVID-19 Precautions",
        "nutritionalReq": "NAS, Low fat, Low cholesterol",
        "nutritionalReqCont": "",
        "edema": "Pedal R/L, Pitting +1",
        "vertigo": False,
        "palpitation": False,
        "can": "true",
        "walker": "true"
    }
}


mainContResponse = {
        "page1": {
            "text1": "Altered status due to Primary osteoarthritis, left shoulder. Knowledge deficit regarding measures to control Primary osteoarthritis, left shoulder and the medication Ibuprofen 600 mg, 1 tablet by mouth every 6 hours as needed for pain as ordered by MD.",
            "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Primary osteoarthritis of the shoulder is a gradual wearing of the articular cartilage that leads to pain and stiffness. As the joint surface degenerates, the subchondral bone remodels, losing its sphericity and congruity. The joint capsule also becomes thickened, leading to further loss of shoulder rotation. Osteoarthritis most often occurs in people who are over age 50. In younger people, it can result from an injury or trauma. SN instructed Patient/PCG regarding the medication Ibuprofen 600 mg. It is used to relieve pain from various conditions and reduces pain, swelling, and joint stiffness caused by arthritis. SN advised Patient/PCG to take medication Ibuprofen 600 mg, 1 tablet by mouth every 6 hours as needed for pain as ordered by MD.",
            "med": "Ibuprofen 600 mg, 1 tablet by mouth every 6 hours as needed for pain",
            "showButton": "1" ,
            "diseaseName": "Fever"
        },
        "page2": {
            "text1": "Altered status due to Primary osteoarthritis. Knowledge deficit regarding measures to control Primary osteoarthritis and the medication Pain Reliever Ointment Gel, apply topically to affected area 2 times daily as ordered by MD.",
            "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Primary osteoarthritis is mostly related to aging. With aging, the water content of the cartilage increases and the protein makeup of cartilage degenerates. Repetitive use of joints over the years causes damage to the cartilage that leads to joint pain and swelling. Arm pain, depending on the location and cause, may be accompanied by numbness, redness, swelling, tenderness, or stiffness of the joints. The goal of treatment in osteoarthritis is to reduce joint pain and inflammation while improving and maintaining joint function. SN instructed Patient/PCG regarding the medication Pain Reliever Ointment Gel. This topical medication is used to relieve pain in the affected joints by applying it directly to the skin. SN advised Patient/PCG to apply Pain Reliever Ointment Gel, apply topically to affected area 2 times daily as ordered by MD.",
            "med": "Pain Reliever Ointment Gel, apply topically to affected area 2 times daily",
            "showButton": "2" ,
            "diseaseName": "Flue"
        },
        "page3": {
            "text1": "Altered status due to Spondylosis w/o myelopathy or radiculopathy. Knowledge deficit regarding measures to control Spondylosis w/o myelopathy or radiculopathy and the medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
            "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Spondylosis w/o myelopathy or radiculopathy is an age-related change of the bones (vertebrae) and discs of the spine. These changes are often called degenerative disc disease and osteoarthritis. These changes don't always cause symptoms. But they are a common cause of spine problems that can range from mild to severe. Spondylosis w/o myelopathy or radiculopathy lumbar region refers to disease involving the lumbar spinal nerve root. This can manifest as pain, numbness, or weakness of the buttock and leg. SN instructed Patient/PCG regarding the medication Rosuvastatin 10 mg. Rosuvastatin is used along with a proper diet to help lower \"bad\" cholesterol and fats in the blood. SN advised Patient/PCG to take medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
            "med": "Rosuvastatin 10 mg, 1 tablet by mouth daily",
            "showButton": "3" ,
            "diseaseName": "Cold"
        },
        "page4": {
            "text1": "Altered status due to Spondylosis w/o myelopathy or radiculopathy. Knowledge deficit regarding measures to control Spondylosis w/o myelopathy or radiculopathy and the medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
            "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Spondylosis w/o myelopathy or radiculopathy is an age-related change of the bones (vertebrae) and discs of the spine. These changes are often called degenerative disc disease and osteoarthritis. These changes don't always cause symptoms. But they are a common cause of spine problems that can range from mild to severe. Spondylosis w/o myelopathy or radiculopathy lumbar region refers to disease involving the lumbar spinal nerve root. This can manifest as pain, numbness, or weakness of the buttock and leg. SN instructed Patient/PCG regarding the medication Rosuvastatin 10 mg. Rosuvastatin is used along with a proper diet to help lower \"bad\" cholesterol and fats in the blood. SN advised Patient/PCG to take medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
            "med": "Rosuvastatin 10 mg, 1 tablet by mouth daily",
            "showButton": "4" ,
            "diseaseName": "Injury"
        },
        "page5": {
            "text1": "Altered status due to Primary osteoarthritis, left shoulder. Knowledge deficit regarding measures to control Primary osteoarthritis, left shoulder and the medication Ibuprofen 600 mg, 1 tablet by mouth every 6 hours as needed for pain as ordered by MD.",
            "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Primary osteoarthritis of the shoulder is a gradual wearing of the articular cartilage that leads to pain and stiffness. As the joint surface degenerates, the subchondral bone remodels, losing its sphericity and congruity. The joint capsule also becomes thickened, leading to further loss of shoulder rotation. Osteoarthritis most often occurs in people who are over age 50. In younger people, it can result from an injury or trauma. SN instructed Patient/PCG regarding the medication Ibuprofen 600 mg. It is used to relieve pain from various conditions and reduces pain, swelling, and joint stiffness caused by arthritis. SN advised Patient/PCG to take medication Ibuprofen 600 mg, 1 tablet by mouth every 6 hours as needed for pain as ordered by MD.",
            "med": "Ibuprofen 600 mg, 1 tablet by mouth every 6 hours as needed for pain",
            "showButton": "1" ,
            "diseaseName": "Muscle Pain"
        },
        "page6": {
            "text1": "Altered status due to Primary osteoarthritis. Knowledge deficit regarding measures to control Primary osteoarthritis and the medication Pain Reliever Ointment Gel, apply topically to affected area 2 times daily as ordered by MD.",
            "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Primary osteoarthritis is mostly related to aging. With aging, the water content of the cartilage increases and the protein makeup of cartilage degenerates. Repetitive use of joints over the years causes damage to the cartilage that leads to joint pain and swelling. Arm pain, depending on the location and cause, may be accompanied by numbness, redness, swelling, tenderness, or stiffness of the joints. The goal of treatment in osteoarthritis is to reduce joint pain and inflammation while improving and maintaining joint function. SN instructed Patient/PCG regarding the medication Pain Reliever Ointment Gel. This topical medication is used to relieve pain in the affected joints by applying it directly to the skin. SN advised Patient/PCG to apply Pain Reliever Ointment Gel, apply topically to affected area 2 times daily as ordered by MD.",
            "med": "Pain Reliever Ointment Gel, apply topically to affected area 2 times daily",
            "showButton": "2" ,
            "diseaseName": "Chemo"
        },
        "page7": {
            "text1": "Altered status due to Spondylosis w/o myelopathy or radiculopathy. Knowledge deficit regarding measures to control Spondylosis w/o myelopathy or radiculopathy and the medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
            "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Spondylosis w/o myelopathy or radiculopathy is an age-related change of the bones (vertebrae) and discs of the spine. These changes are often called degenerative disc disease and osteoarthritis. These changes don't always cause symptoms. But they are a common cause of spine problems that can range from mild to severe. Spondylosis w/o myelopathy or radiculopathy lumbar region refers to disease involving the lumbar spinal nerve root. This can manifest as pain, numbness, or weakness of the buttock and leg. SN instructed Patient/PCG regarding the medication Rosuvastatin 10 mg. Rosuvastatin is used along with a proper diet to help lower \"bad\" cholesterol and fats in the blood. SN advised Patient/PCG to take medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
            "med": "Rosuvastatin 10 mg, 1 tablet by mouth daily",
            "showButton": "3" ,
            "diseaseName": "Hepatites"
        },
        "page8": {
            "text1": "Altered status due to Spondylosis w/o myelopathy or radiculopathy. Knowledge deficit regarding measures to control Spondylosis w/o myelopathy or radiculopathy and the medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
            "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Spondylosis w/o myelopathy or radiculopathy is an age-related change of the bones (vertebrae) and discs of the spine. These changes are often called degenerative disc disease and osteoarthritis. These changes don't always cause symptoms. But they are a common cause of spine problems that can range from mild to severe. Spondylosis w/o myelopathy or radiculopathy lumbar region refers to disease involving the lumbar spinal nerve root. This can manifest as pain, numbness, or weakness of the buttock and leg. SN instructed Patient/PCG regarding the medication Rosuvastatin 10 mg. Rosuvastatin is used along with a proper diet to help lower \"bad\" cholesterol and fats in the blood. SN advised Patient/PCG to take medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
            "med": "Rosuvastatin 10 mg, 1 tablet by mouth daily",
            "showButton": "4" ,
            "diseaseName": "sweating"
        },
        "page9": {
            "text1": "Altered status due to Spondylosis w/o myelopathy or radiculopathy. Knowledge deficit regarding measures to control Spondylosis w/o myelopathy or radiculopathy and the medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
            "text2": "SN admitted the patient for comprehensive skilled nursing assessment, observation and evaluation of all body systems. SN to assess vital signs, pain level. SN performed to check vital signs and scale pain (1-10) every visit. SN to evaluate therapeutic response to current/new medications and compliance to medication/diet regimen, home safety issues and psychosocial adjustment. Spondylosis w/o myelopathy or radiculopathy is an age-related change of the bones (vertebrae) and discs of the spine. These changes are often called degenerative disc disease and osteoarthritis. These changes don't always cause symptoms. But they are a common cause of spine problems that can range from mild to severe. Spondylosis w/o myelopathy or radiculopathy lumbar region refers to disease involving the lumbar spinal nerve root. This can manifest as pain, numbness, or weakness of the buttock and leg. SN instructed Patient/PCG regarding the medication Rosuvastatin 10 mg. Rosuvastatin is used along with a proper diet to help lower \"bad\" cholesterol and fats in the blood. SN advised Patient/PCG to take medication Rosuvastatin 10 mg, 1 tablet by mouth daily as ordered by MD.",
            "med": "Rosuvastatin 10 mg, 1 tablet by mouth daily",
            "showButton": "4" ,
            "diseaseName": "laziness"
        }
    }

diseaseList = ['Primary osteoarthritis, left shoulder', 'Primary osteoarthritis, right', 'Spondylosis w/o myelopathy or radiculopathy', 'Essential (primary) hypertension', 'Unspecified asthma, uncomplicated', 'Edema, unspecified', 'Weakness', 'Iron deficiency anemia, unspecified', 'Hyperlipidemia, unspecified', 'Vitamin D deficiency, unspecified', 'History of falling']

def get_extracted_data_storage():
    return copy.deepcopy(extracted_data_storage)

def get_mainContResponse():
    return copy.deepcopy(mainContResponse)

def get_diseaseList():
    return copy.deepcopy(diseaseList)