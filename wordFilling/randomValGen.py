import random

# Set fixed initial values for each run
INITIAL_BS_FAST = 180  # Starting value for bsFast
INITIAL_BS_RAPID = INITIAL_BS_FAST + 30  # Ensure a 30 difference

def get_random_bp(systolic_min=130, systolic_max=145, diastolic_min=65, diastolic_max=87):
    systolic = random.randint(systolic_min, systolic_max)
    diastolic = random.randint(diastolic_min, diastolic_max)
    return f"{systolic}/{diastolic}"

def get_random_value(min_value, max_value, roundTo=1, is_integer=False):
    value = random.uniform(min_value, max_value)
    if is_integer:
        return round(value)
    return round(value, roundTo)

def get_decreasing_bs_values(previous_bsFast, previous_bsRapid):
    """
    Generates decreasing values for bsFast and ensures bsRapid remains exactly 30 units higher.
    """
    # Set minimum limits
    min_bsFast = 100
    min_bsRapid = 130  # Must remain 30 higher than min_bsFast

    # Choose a random decrease with weighted probability
    decrease = random.choices([1, 2, 3, 4], weights=[0.4, 0.35, 0.15, 0.1])[0]
    # Ensure the decrease does not go below minimum limits
    bsFastVal = max(previous_bsFast - decrease, min_bsFast)
    bsRapidVal = bsFastVal + 30  # Maintain a strict 30 difference


    return bsFastVal, bsRapidVal

def getRangeValues(previous_bsFast, previous_bsRapid):
    tempVal = str(get_random_value(97.7, 99.5))
    hrVal = str(get_random_value(60, 100, is_integer=True))
    rrVal = str(get_random_value(16, 20, is_integer=True))
    oxygenVal = str(get_random_value(95, 99, is_integer=True))
    
    # Get decreasing blood sugar values
    bsFastVal, bsRapidVal = get_decreasing_bs_values(previous_bsFast, previous_bsRapid)
    
    random_bp = str(get_random_bp())
    return tempVal, hrVal, rrVal, oxygenVal, bsFastVal, bsRapidVal, random_bp

def getRangeValuesArray(noOfVal):
    # Generate arrays for n iterations.
    tempArray = []
    hrArray = []
    rrArray = []
    oxygenArray = []
    bsFastArray = []
    bsRapidArray = []
    random_bpArray = []

    previous_bsFast = INITIAL_BS_FAST  # Reset at the start of each run
    previous_bsRapid = INITIAL_BS_RAPID
    
    for i in range(noOfVal):
        tempVal, hrVal, rrVal, oxygenVal, bsFastVal, bsRapidVal, random_bp = getRangeValues(previous_bsFast, previous_bsRapid)
        tempArray.append(tempVal)
        hrArray.append(hrVal)
        rrArray.append(rrVal)
        oxygenArray.append(oxygenVal)
        bsFastArray.append(str(bsFastVal))
        bsRapidArray.append(str(bsRapidVal))
        random_bpArray.append(random_bp)
        # Update previous values
        previous_bsFast = bsFastVal
        previous_bsRapid = bsRapidVal

    return tempArray, hrArray, rrArray, oxygenArray, bsFastArray, bsRapidArray, random_bpArray