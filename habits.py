from validators import *
from datetime import datetime

def add_habit(data, habit_name, target):
    habit_name = validate_string(habit_name, 3, 20)
    created_at = datetime.now().date().isoformat()

    if habit_name in data["habits"]:
        if data["habits"][habit_name].get("archived_at") is not None:
            raise ValueError("Habit exists but is archived.")
        else:
            raise ValueError("Habit already exists.")
    
    target = validate_int(target, 1)

    habit_info = {
        "target_per_week": target,
        "created_at": created_at,
        "archived_at": None
    }

    habits = data["habits"]
    habits[habit_name] = habit_info

    return f"{habit_name} added."

def log_habit(data, habit_name, log_date):
    today = datetime.now().date()

    if not log_date:
        log_date = today
    else:
        log_date = validate_date(log_date)

    if log_date > today:
        raise ValueError("Cannot log a future habit.")
    
    habit_name = validate_string(habit_name, 3, 20)

    if habit_name not in data["habits"]:
        raise ValueError("Habit does not exist.")
    
    if data["habits"][habit_name].get("archived_at") is not None:
        raise ValueError("Cannot log as the habit is archived.")
    
    created_date = data["habits"][habit_name]["created_at"]
    created_date = validate_date(created_date)
    
    if log_date < created_date:
        raise ValueError("Habit cannot be logged before it was created.")
      
    log_date = log_date.isoformat()
    logs = data["logs"]

    if any(
        log["habit"] == habit_name and log["date"] == log_date
        for log in logs
    ):
        raise ValueError("Habit already logged for this date.")

    data["logs"].append({
        "habit": habit_name,
        "date": log_date
    })

    return f"{habit_name} logged for {log_date}."

def archive_habit(data, habit_name):
    habit_name = validate_string(habit_name, 3, 20)

    if habit_name not in data["habits"]:
        raise ValueError("Habit does not exist.")
    
    if data["habits"][habit_name].get("archived_at") is not None:
        raise ValueError("Habit already archived.")
    
    today = datetime.now().date().isoformat()
    data["habits"][habit_name]["archived_at"] = today
    return f"{habit_name} archived."

def unarchive_habit(data, habit_name):
    habit_name = validate_string(habit_name, 3, 20)

    if habit_name not in data["habits"]:
        raise ValueError("Habit does not exist.")
    
    if data["habits"][habit_name].get("archived_at") is None:
        raise ValueError("Habit already active.")
    
    data["habits"][habit_name]["archived_at"] = None
    return f"{habit_name} unarchived."

def delete_habit(data, habit_name):
    habit_name = validate_string(habit_name, 3, 20)

    if habit_name not in data["habits"]:
        raise ValueError("Habit does not exist.")

    data["logs"] = [
        log for log in data["logs"]
        if log["habit"] != habit_name
    ]

    del data["habits"][habit_name]
    return f"{habit_name} deleted."

# this sorts logs by date
# data["logs"].sort(key=lambda x: x["date"])