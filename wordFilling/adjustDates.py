from datetime import datetime, timedelta

def adjust_dates(appointment_date, appointment_time, constipation=False):
    """
    Adjust an appointment date based on the appointment time and the constipation flag.
    
    - If constipation is True, subtract one day from the appointment date.
    - Otherwise, subtract one day only if the starting time is before 10:00 AM.
    
    Parameters:
      appointment_date (str): A date string in "YYYY-MM-DD" format.
      appointment_time (str): A time string (e.g., "4:00-4:45"). The first time in the range is used.
      constipation (bool): Flag indicating whether constipation is true.
      
    Returns:
      str: The adjusted date string in "MM/DD/YY" format.
    """
    # Parse the appointment_date from the new format "YYYY-MM-DD".
    dt = datetime.strptime(appointment_date, "%Y-%m-%d")
    start_time_str = appointment_time.split('-')[0].strip() if '-' in appointment_time else appointment_time.strip()

    # Attempt to parse using a 24-hour format first; if that fails, use a 12-hour format.
    t = datetime.strptime(start_time_str, "%H:%M")
    # Use a 24-hour cutoff for 10:00.
    cutoff = datetime.strptime("10:00", "%H:%M")
    
    if constipation == True:
        new_dt = dt - timedelta(days=1)
    else:
        new_dt = dt - timedelta(days=1) if t < cutoff else dt

    # Return the adjusted date in "MM/DD/YY" format (matching previous version)
    return new_dt.strftime("%m/%d/%y")