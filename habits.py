from utils import parse_date
from datetime import datetime

def add_habit(data, habit_name, target_per_week):
    created_at = datetime.now().date().isoformat()

    habit_info = {
        "target_per_week": target_per_week,
        "created_at": created_at,
        "archived_at": None
    }

    habits = data["habits"]
    habits[habit_name] = habit_info

    return True, "Habit added."

def archive_habit(data, habit_name):
    today = datetime.now().date().isoformat()
    data["habits"][habit_name]["archived_at"] = today
    return True, "Habit archived."

def unarchive_habit(data, habit_name):
    data["habits"][habit_name]["archived_at"] = None
    return True, "Habit unarchived."

def delete_habit(data, habit_name):

    data["logs"] = [
        log for log in data["logs"]
        if log["habit"] != habit_name
    ]

    del data["habits"][habit_name]

    return True, "Habit deleted."

def log_habit(data, habit_name, log_date):
        
    created_date = data["habits"][habit_name]["created_at"]
    created_date = parse_date(created_date)
        
    if log_date < created_date:
        return False, "Habit cannot be logged before it was created."
    
    today = datetime.now().date()
    if log_date > today:
        return False, "Cannot log a future habit."
        
    log_date = log_date.isoformat()

    logs = data["logs"]

    if any(
        log["habit"] == habit_name and log["date"] == log_date
        for log in logs
    ):
        return False, "Habit already logged for this date."

    data["logs"].append({
        "habit": habit_name,
        "date": log_date
    })

    return True, "Habit logged."

# this sorts logs by date
# data["logs"].sort(key=lambda x: x["date"])