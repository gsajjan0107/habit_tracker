from validators import validate_string, validate_int, validate_date
from helpers import get_today, habit_exists, is_habit_archived
from helpers import make_result, display_message

def add_habit(data, habit_name, target):
    habit_name = validate_string(habit_name, 3, 20)
    created_at = get_today().isoformat()

    if habit_exists(data, habit_name):
        if is_habit_archived(data, habit_name):
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

def log_habit(data, log_date, habit_name):
    if not data["habits"]:
        display_message("No habits found. Add a habit first.")
        return
    
    log_date = validate_date(log_date)
    
    habit_name = validate_string(habit_name, 3, 20)

    if not habit_exists(data, habit_name):
        raise ValueError("Habit does not exist.")
    
    if is_habit_archived(data, habit_name):
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

def log_multiple_habits(data, log_date, habits):
    logged = []
    for habit_name in habits:
        log_habit(data, log_date, habit_name)
        logged.append(habit_name)

    return logged

def delete_log(data, log_date, habit_name):
    if not data["habits"]:
        return "No habits found. Add a habit first."
        
    if not data["logs"]:
        return "No logs found. Log a habit first."        

    before = len(data["logs"])
    
    log_date = validate_date(log_date)
    log_date = log_date.isoformat()
    
    data["logs"] = [
        log for log in data["logs"]
        if not (log["habit"] == habit_name and log["date"] == log_date)
    ]

    after = len(data["logs"])
        
    if before == after:
        return "No matching log found."
    else:
        return f"Log of {habit_name} for {log_date} deleted."

def archive_habit(data, habit_name, archived_at=None):
    habit_name = validate_string(habit_name, 3, 20)

    if not habit_exists(data, habit_name):
        return make_result(False, "Habit does not exist.", {"habit": habit_name})

    if is_habit_archived(data, habit_name):
        return make_result(False, "Habit already archived.", {"habit": habit_name, "archived": True})
    
    if archived_at is None:
        archived_date = get_today()
    else:
        archived_date = validate_date(archived_at)

    created_date = validate_date(data["habits"][habit_name]["created_at"])

    if archived_date < created_date:
        return make_result(False, "Habit cannot be archived before it was created.", {"habit": habit_name})

    data["habits"][habit_name]["archived_at"] = archived_date.isoformat()

    return make_result(True, f"{habit_name} archived.", {"habit": habit_name, "archived": True})

def unarchive_habit(data, habit_name):
    habit_name = validate_string(habit_name, 3, 20)

    if not habit_exists(data, habit_name):
        return make_result(False, "Habit does not exist.", {"habit": habit_name})
    
    if not is_habit_archived(data, habit_name):
        return make_result(False, "Habit already active.", {"habit": habit_name, "archived": False})
    
    data["habits"][habit_name]["archived_at"] = None

    return make_result(True, f"{habit_name} unarchived.", {"habit": habit_name, "archived": False})

def toggle_archive_habit(data, habit_name):
    habit_name = validate_string(habit_name, 3, 20)

    if not habit_exists(data, habit_name):
        return make_result(False, "Habit does not exist.", {"habit": habit_name})

    if is_habit_archived(data, habit_name):
        return unarchive_habit(data, habit_name)

    return archive_habit(data, habit_name)

def delete_habit(data, habit_name):
    habit_name = validate_string(habit_name, 3, 20)

    if not habit_exists(data, habit_name):
        raise ValueError("Habit does not exist.")

    data["logs"] = [
        log for log in data["logs"]
        if log["habit"] != habit_name
    ]

    del data["habits"][habit_name]
    return f"{habit_name} deleted."

# this sorts logs by date
# data["logs"].sort(key=lambda x: x["date"])