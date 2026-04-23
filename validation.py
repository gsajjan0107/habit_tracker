from utils import parse_date
from datetime import datetime

def validate_data_structure(data):

    if not isinstance(data, dict):
        return False, "'data' is not a dictionary."

    if "habits" not in data:
        return False, "key 'habits' does not exist in 'data'."
    
    if "logs" not in data:
        return False, "key 'logs' does not exist in 'data'."

    if not isinstance(data["habits"], dict):
        return False, "data['habits'] is not a dictionary."

    if not isinstance(data["logs"], list):
        return False, "data['logs'] is not a list."

    success, msg = validate_habits_data_structure(data)
    if not success:
        return False, msg
    
    success, msg = validate_logs_data_structure(data)
    if not success:
        return False, msg

    return True, "validation of data structure successful."

def validate_habits_data_structure(data):

    habits = data["habits"]

    for habit, habit_data in habits.items():

        if not isinstance(habit_data, dict):
            return False, f"data['habits'][{habit}] is not a dictionary."

        target = habit_data.get("target_per_week")
        if not isinstance(target, int) or target <= 0:
            return False, f"target per week of {habit} is not an integer more than 0."

        created_at = habit_data.get("created_at")
        try:
            created = parse_date(created_at)
        except ValueError:
            return False, f"'created_at' date of {habit} is not a valid date." 

        archived_at = habit_data.get("archived_at")
        if archived_at is not None:
            
            try:
                archived = parse_date(archived_at)
            except ValueError:
                return False, f"'archived_at' of {habit} must be None or a valid date."
            
            if archived < created:
                return False, f"'archived_at' date of {habit} cannot be before its 'created_at' date."

    return True, "validation of data['habits'] successful."

def validate_logs_data_structure(data):
    logs = data["logs"]
    habits = data["habits"]

    seen = set()  # Track (habit, date) pairs to prevent duplicates

    for log in logs:

        if not isinstance(log, dict):
            return False, f"{log} in logs is not a dictionary."

        habit = log.get("habit")
        if not isinstance(habit, str) or not habit:
            return False, f"'habit' field in log {log} must be a non-empty string."
        
        if habit not in habits:
            return False, f"{habit} name in a {log}, does not exist."

        date = log.get("date")
        try:
            date = parse_date(date)
        except ValueError:
            return False, f"{date} in {log} is not valid."
        
        if date > datetime.now().date():
            return False, f"{date} in {log} cannot be in the future."

        key = (habit, date)
        if key in seen:
            return False, f"duplicate log found: {log}."

        seen.add(key)

    return True, "validation of data['logs'] successful."