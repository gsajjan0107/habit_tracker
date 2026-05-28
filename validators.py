from datetime import datetime, date
from helpers import get_today, display_message
import re # for validate_string

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
        
        if "target_per_week" not in habit_data:
            return False, f"habits['{habit}'].target_per_week → missing key."

        if "created_at" not in habit_data:
            return False, f"habits['{habit}'].created_at → missing key."
        
        if "archived_at" not in habit_data:
            return False, f"habits['{habit}'].archived_at → missing key."
        
        target = habit_data["target_per_week"]
        created_at = habit_data["created_at"]
        archived_at = habit_data["archived_at"]

        required_keys = {"target_per_week", "created_at", "archived_at"}
        
        if set(habit_data.keys()) != required_keys:
            return False, f"habits['{habit}'] → invalid keys."
        
        if not isinstance(target, int) or target <= 0:
            return False, f"habits['{habit}'].target_per_week → expected int > 0."
        
        try:
            created = validate_date(created_at)
        except ValueError:
            return False, f"habits['{habit}'].created_at → invalid date format (YYYY-MM-DD)." 

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

    seen = set()

    for i, log in enumerate(logs):

        if not isinstance(log, dict):
            return False, f"logs[{i}] → expected dict."

        if "habit" not in log:
            return False, f"logs[{i}].habit → missing key."

        habit = log["habit"]

        if habit not in data["habits"]:
            return False, f"logs[{i}].habit → habit '{habit}' does not exist."

        if not isinstance(habit, str) or not habit:
            return False, f"logs[{i}].habit → expected non-empty string."
        
        if habit not in habits:
            return False, f"logs[{i}].habit → '{habit}' not found in habits."

        if "date" not in log:
            return False, f"logs[{i}].date → missing key."
        
        try:
            date = validate_date(log["date"])
        except ValueError:
            return False, f"logs[{i}].date → invalid date format (YYYY-MM-DD)."
        
        created = validate_date(habits[habit]["created_at"])

        if date < created:
            return False, f"logs[{i}] → date before habit creation."
        
        archived_at = habits[habit].get("archived_at")

        if archived_at is not None:
            archived = validate_date(archived_at)

            if date > archived:
                return False, f"logs[{i}] → date after habit archive."

        key = (habit, date)

        if key in seen:
            return False, f"logs[{i}] → duplicate entry for ({habit}, {date})."

        seen.add(key)

    return True, None

def get_valid_input(prompt: str, validator):
    """Prompt user until valid input is entered and return validated result."""
    while True:
        value = input(prompt).strip()
        try:
            return validator(value)
        except ValueError as e:
            display_message(f"Error: {e}")

def validate_int(value: str, min_val=None, max_val=None) -> int:
    """Convert input to int and enforce optional minimum and maximum limits."""
    try:
        num = int(value)
    except ValueError:
        raise ValueError(f"Input must be an integer.")
    
    if min_val is not None and num < min_val:
        raise ValueError(f"Input number must be >= {min_val}")
    
    if max_val is not None and num > max_val:
        raise ValueError(f"Input number must be <= {max_val}")
    
    return num

def validate_string(value: str, min_len=1, max_len=None) -> str:
    """Validate text length and allow letters, spaces, and selected symbols."""
    value = value.strip()

    if not value:
        raise ValueError("Cannot be empty.")
    
    if len(value) < min_len:
        raise ValueError(f"Minimum {min_len} characters required.")
    
    if max_len is not None and len(value) > max_len:
        raise ValueError(f"Maximum {max_len} characters allowed.")
    
    if not re.match(r"^[A-Za-z /$_:\-]+$", value):
        raise ValueError("Only letters, spaces, and / $ - _ : allowed.")
    
    return value.title()

def validate_choice(value: str, choices: list[str]) -> str:
    """Validate input against allowed choices and return normalized value."""
    value = value.strip().lower()

    if value not in choices:
        raise ValueError(f"Choose from {choices}")
    
    return value

def validate_date(value):
    today = get_today()

    if value is None:
        return today

    if isinstance(value, datetime):
        value = value.date()

    elif isinstance(value, date):
        pass

    elif isinstance(value, str):
        value = value.strip()

        if value == "":
            return today

        try:
            value = datetime.strptime(value, "%Y-%m-%d").date()

        except ValueError:
            raise ValueError("Use format YYYY-MM-DD (e.g., 2026-04-25)")

    else:
        raise ValueError("Date must be a string in format YYYY-MM-DD.")

    if value > today:
        raise ValueError("Cannot accept future date.")

    return value