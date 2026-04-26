from datetime import datetime
from validators import *

def validate_data_structure(data):

    if not isinstance(data, dict):
        return False, "data → expected dict, got something else."

    if "habits" not in data:
        return False, "data.habits → missing key."
    
    if "logs" not in data:
        return False, "data.logs → missing key."

    if not isinstance(data["habits"], dict):
        return False, "data.habits → expected dict."

    if not isinstance(data["logs"], list):
        return False, "data.logs → expected list."

    success, msg = validate_habits_data_structure(data)
    if not success:
        return False, msg
    
    success, msg = validate_logs_data_structure(data)
    if not success:
        return False, msg

    return True, None

def validate_habits_data_structure(data):

    habits = data["habits"]

    for habit, habit_data in habits.items():

        if not isinstance(habit_data, dict):
            return False, f"habits['{habit}'] → expected dict."

        target = habit_data.get("target_per_week")
        if not isinstance(target, int) or target <= 0:
            return False, f"habits['{habit}'].target_per_week → expected int > 0."

        created_at = habit_data.get("created_at")
        try:
            created = validate_date(created_at)
        except ValueError:
            return False, f"habits['{habit}'].created_at → invalid date format (YYYY-MM-DD)." 

        archived_at = habit_data.get("archived_at")
        if archived_at is not None:
            
            try:
                archived = validate_date(archived_at)
            except ValueError:
                return False, f"habits['{habit}'].archived_at → must be None or valid date."
            
            if archived < created:
                return False, f"habits['{habit}'] → archived_at cannot be before created_at."

    return True, None

def validate_logs_data_structure(data):
    logs = data["logs"]
    habits = data["habits"]

    seen = set()  # Track (habit, date) pairs to prevent duplicates
    today = datetime.now().date()
    for i, log in enumerate(logs):

        if not isinstance(log, dict):
            return False, f"logs[{i}] → expected dict."

        habit = log.get("habit")
        if not isinstance(habit, str) or not habit:
            return False, f"logs[{i}].habit → expected non-empty string."
        
        if habit not in habits:
            return False, f"logs[{i}].habit → '{habit}' not found in habits."

        date = log.get("date")
        try:
            date = validate_date(date)
        except ValueError:
            return False, f"logs[{i}].date → invalid date format (YYYY-MM-DD)."
        
        if date > today:
            return False, f"logs[{i}].date → cannot be in the future."
        
        created = validate_date(habits[habit]["created_at"])        
        if date < created:
            return False, f"logs[{i}] → date before habit creation."

        key = (habit, date)
        if key in seen:
            return False, f"logs[{i}] → duplicate entry for ({habit}, {date})."

        seen.add(key)

    return True, None