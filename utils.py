from datetime import datetime

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()
    
def normalize_habit_name(habit_name):
    return habit_name.strip().lower()

def get_valid_habit_name(habit_name):
    habit_name = habit_name.strip().lower()

    if not habit_name:
        return False, "Habit name cannot be empty."
    
    return True, habit_name
    
def get_habit_exist_status(data, habit_name):
    
    if habit_name in data["habits"]:
        return True, "Habit exists."
    else:
        return False, "Habit does not exist."
    
def get_habit_archive_status(data, habit_name):
    if data["habits"][habit_name]["archived_at"] is not None:
        return True, "Habit is acrhived."
    else:
        return False, "Habit is not archived."
    