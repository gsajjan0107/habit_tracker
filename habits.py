from validators import validate_string, validate_int, validate_date
from helpers import get_today, habit_exists, is_habit_archived
from helpers import make_result, habit_has_logs

def add_habit(data, habit_name, target, description=""):
    habit_name = validate_string(habit_name, 3, 20)

    if habit_exists(data, habit_name):
        if is_habit_archived(data, habit_name):
            raise ValueError("Habit exists but is archived. Unarchive it instead.")
        else:
            raise ValueError("Habit already exists.")

    target = validate_int(target, 1)
    created_at = get_today().isoformat()
    description = description.strip()

    habit_info = {
        "target_per_week": target,
        "created_at": created_at,
        "archived_at": None,
        "description": description
    }

    habits = data["habits"]
    habits[habit_name] = habit_info

    return f"{habit_name} added."

def log_habit(data, log_date, habit_name, note=""):
    if not data["habits"]:
        raise ValueError("No habits found. Add a habit first.")

    log_date = validate_date(log_date)

    habit_name = validate_string(habit_name, 3, 20)

    if not habit_exists(data, habit_name):
        raise ValueError("Habit does not exist.")

    archived_at = data["habits"][habit_name].get("archived_at")

    if archived_at is not None:
        archived_date = validate_date(archived_at)

        if log_date > archived_date:
            raise ValueError("Cannot log after the habit was archived.")

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
        "date": log_date,
        "note": note
        })

    return f"{habit_name} logged for {log_date}."

def log_multiple_habits(data, log_date, habits, notes):
    original_logs = data["logs"].copy()

    logged = []

    try:
        for habit_name in habits:
            note = notes.get(habit_name, "")
            log_habit(data, log_date, habit_name, note)
            logged.append(habit_name)

    except ValueError:
        data["logs"] = original_logs
        raise

    return logged

def delete_log(data, log_date, habit_name):
    if not data["habits"]:
        raise ValueError("No habits found. Add a habit first.")

    habit_name = validate_string(habit_name, 3, 20)

    if not habit_exists(data, habit_name):
        raise ValueError("Habit does not exist.")

    if not data["logs"]:
        raise ValueError("No logs found. Log a habit first.")

    before = len(data["logs"])

    log_date = validate_date(log_date)
    log_date = log_date.isoformat()

    data["logs"] = [
        log for log in data["logs"]
        if not (log["habit"] == habit_name and log["date"] == log_date)
    ]

    after = len(data["logs"])

    if before == after:
        raise ValueError("No matching log found.")

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

    if habit_has_logs(data, habit_name):
        raise ValueError("Cannot permanently delete a habit with existing logs. Archive it instead.")

    del data["habits"][habit_name]
    return f"{habit_name} deleted."

def rename_habit(data, old_name, new_name):
    old_name = validate_string(old_name, 3, 20)
    new_name = validate_string(new_name, 3, 20)

    if not habit_exists(data, old_name):
        raise ValueError("Habit does not exist.")

    if habit_exists(data, new_name):
        raise ValueError("Habit already exists.")

    data["habits"][new_name] = data["habits"].pop(old_name)

    for log in data["logs"]:
        if log["habit"] == old_name:
            log["habit"] = new_name

    return f"{old_name} renamed to {new_name}."

def update_habit_target(data, habit_name, target_per_week):
    habit_name = validate_string(habit_name, 3, 20)
    target = validate_int(target_per_week, 1)

    if not habit_exists(data, habit_name):
        raise ValueError("Habit does not exist.")

    data["habits"][habit_name]["target_per_week"] = target

    return f"{habit_name} target updated to {target} per week."

def get_habit_logs(data, habit_name):
    habit_name = validate_string(habit_name, 3, 20)

    if not habit_exists(data, habit_name):
        raise ValueError("Habit does not exist.")

    dates = []

    for log in data["logs"]:
        if log["habit"] == habit_name:
            dates.append(log["date"])

    return sorted(dates, reverse=True)

def update_habit_description(data, habit_name, description):
    habit_name = validate_string(habit_name, 3, 20)

    if not habit_exists(data, habit_name):
        raise ValueError("Habit does not exist.")

    if not isinstance(description, str):
        raise ValueError("Input must be a string.")

    description = description.strip()
    data["habits"][habit_name]["description"] = description

    return f"{habit_name} description updated."