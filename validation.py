from utils import parse_date, valid_date

def validate_data_structure(data):

    if not isinstance(data, dict):
        return False

    if not all(key in data for key in ("habits", "logs")):
        return False

    if not isinstance(data["habits"], dict):
        return False

    if not isinstance(data["logs"], list):
        return False

    if not validate_habits_data_structure(data):
        return False

    if not validate_logs_data_structure(data):
        return False

    return True

def validate_habits_data_structure(data):

    habits = data["habits"]

    for habit_data in habits.values():

        if not isinstance(habit_data, dict):
            return False

        target = habit_data.get("target_per_week")
        if not isinstance(target, int) or target <= 0:
            return False

        created_at = habit_data.get("created_at")
        if not valid_date(created_at):
            return False

        archived_at = habit_data.get("archived_at")
        if archived_at is not None:
            if not valid_date(archived_at):
                return False
            if parse_date(archived_at) < parse_date(created_at):
                return False

    return True

def validate_logs_data_structure(data):
    logs = data["logs"]
    habits = data["habits"]

    seen = set()  # Track (habit, date) pairs to prevent duplicates

    for log in logs:

        if not isinstance(log, dict):
            return False

        habit = log.get("habit")
        if not isinstance(habit, str) or not habit:
            return False
        
        if habit not in habits:
            return False

        date = log.get("date")

        if not valid_date(date):
            return False

        key = (habit, date)
        if key in seen:
            return False

        seen.add(key)

    return True