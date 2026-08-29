from datetime import datetime, date
from helpers import get_today, display_message
import re # for validate_string
from config import VALID_DAYS, DEFAULT_SCHEDULED_DAYS

def validate_keys(dict_data, required_keys, path):
    actual_keys = set(dict_data)

    missing = set(required_keys) - actual_keys
    unexpected = actual_keys - set(required_keys)

    if missing:
        for key in required_keys:
            if key not in actual_keys:
                return False, f"{path}.{key} → missing key."

    if unexpected:
        return False, f"{path} → invalid keys: '{next(iter(unexpected))}'."

    return True, None

def validate_data_structure(data):

    if not isinstance(data, dict):
        return False, "data → expected dict, got something else."

    required_keys = {"schema_version", "habits", "logs"}
    success, msg = validate_keys(data, required_keys, "data")

    if not success:
        return False, msg

    if not isinstance(data["schema_version"], int):
        return False, "schema_version → expected int."

    if data["schema_version"] != 1:
        return False, "schema_version → unsupported version."

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
    seen_ids = set()

    for habit, habit_data in habits.items():

        if not isinstance(habit_data, dict):
            return False, f"habits['{habit}'] → expected dict."

        required_keys = ("id", "target_per_week", "created_at", "archived_at", "description", "scheduled_days")
        success, msg = validate_keys(habit_data, required_keys, f"habits['{habit}']")

        if not success:
            return False, msg

        habit_id = habit_data["id"]
        target = habit_data["target_per_week"]
        created_at = habit_data["created_at"]
        archived_at = habit_data["archived_at"]
        description = habit_data["description"]
        scheduled_days = habit_data["scheduled_days"]

        if not isinstance(habit_id, int) or habit_id < 1:
            return False, f"habits['{habit}'].id → expected int >= 1."

        if habit_id in seen_ids:
            return False, f"habits['{habit}'].id → duplicate id ({habit_id})."

        seen_ids.add(habit_id)

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

        if not isinstance(description, str):
            return False, f"habits['{habit}'].description → expected string."

        if not isinstance(scheduled_days, list):
            return False, f"habits['{habit}'].scheduled_days → expected list."

        if not scheduled_days:
            return False, f"habits['{habit}'].scheduled_days → cannot be empty."

        for day in scheduled_days:
            if not isinstance(day, str):
                return False, f"habits['{habit}'].scheduled_days contains non-string value."

            if day not in VALID_DAYS:
                return False, f"habits['{habit}'].scheduled_days → invalid day: '{day}'."

        if len(scheduled_days) != len(set(scheduled_days)):
            return False, f"habits['{habit}'].scheduled_days cannot have duplicates."

        if len(scheduled_days) < target:
            return False, f"habits['{habit}'].scheduled_days → cannot be fewer than target_per_week."

    return True, None

def validate_logs_data_structure(data):
    logs = data["logs"]
    habits = data["habits"]

    seen = set()

    for i, log in enumerate(logs):

        if not isinstance(log, dict):
            return False, f"logs[{i}] → expected dict."

        required_keys = ("habit", "date", "note")
        success, msg = validate_keys(log, required_keys, f"logs[{i}]")

        if not success:
            return False, msg

        habit = log["habit"]

        if not isinstance(habit, str) or not habit:
            return False, f"logs[{i}].habit → expected non-empty string."

        if habit not in habits:
            return False, f"logs[{i}].habit → habit '{habit}' does not exist."

        try:
            date = validate_date(log["date"])
        except ValueError:
            return False, f"logs[{i}].date → invalid date format (YYYY-MM-DD)."

        created = validate_date(habits[habit]["created_at"])

        if date < created:
            return False, f"logs[{i}] → date before habit creation."

        archived_at = habits[habit]["archived_at"]

        if archived_at is not None:
            archived = validate_date(archived_at)

            if date > archived:
                return False, f"logs[{i}] → date after habit archive."

        note = log["note"]

        if not isinstance(note, str):
            return False, f"logs[{i}].note → expected string."

        key = (habit, date)

        if key in seen:
            return False, f"logs[{i}] → duplicate entry for ({habit}, {date})."

        seen.add(key)

    return True, None

def validate_int(value: str, min_val=None, max_val=None) -> int:
    """Convert value to an integer and check its range."""
    try:
        num = int(value)
    except ValueError:
        raise ValueError("Input must be an integer.")

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

def validate_date(value):
    """Validate a date and return it as a date object."""
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
            raise ValueError("Use format YYYY-MM-DD format (e.g., 2026-04-25)")

    else:
        raise ValueError("Use format YYYY-MM-DD format (e.g., 2026-04-25)")

    if value > today:
        raise ValueError("Cannot accept future date.")

    return value

def get_valid_input(prompt: str, validator):
    """Prompt user until valid input is entered and return validated result."""
    while True:
        value = input(prompt).strip()
        try:
            return validator(value)
        except ValueError as e:
            display_message(f"Error: {e}")

def validate_choice(value: str, choices: list[str]) -> str:
    """Validate input against allowed choices and return normalized value."""
    value = value.strip().lower()

    if value not in choices:
        raise ValueError(f"Choose from {choices}")

    return value

def validate_scheduled_days(scheduled_days):

    if not isinstance(scheduled_days, list):
        raise ValueError("scheduled_days must be a list.")

    if not scheduled_days:
        raise ValueError("scheduled_days is empty.")

    if not all(day in VALID_DAYS for day in scheduled_days):
        raise ValueError("scheduled_days contains an invalid day.")

    return [day for day in DEFAULT_SCHEDULED_DAYS if day in scheduled_days]