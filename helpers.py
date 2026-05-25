from datetime import datetime

def format_display_date(date_str):
    """Convert YYYY-MM-DD into a cleaner display format: 2026-05-08 -> 08 May 2026"""

    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%d %b %Y")

def display_numbered_list(items):
    for i, item in enumerate(items, start=1):
        display_message(f"{i}. {item}")

def show_habits_status(result):
    pending = result["pending"]
    completed = result["completed"]

    if completed:
        display_message("\n✅ Completed:")
        display_numbered_list(completed)

    if pending:
        display_message("\n🚫 Unfinished:")
        display_numbered_list(pending)

def get_confirmation(message):
    while True:
        confirm = input(message).strip().lower()

        if confirm in ["y", "yes"]:
            return True

        if confirm in ["n", "no"]:
            return False

        display_message("Please enter y/yes or n/no.")

def get_today():
    return datetime.now().date()

def habit_exists(data, habit_name):
    return data["habits"].get(habit_name)

def is_habit_archived(data, habit_name):
    return (data["habits"][habit_name].get("archived_at") is not None)

def ensure_habits_exist(data):
    if not data["habits"]:
        display_message("No habits found. Add a habit first.")
        return False

    return True

def display_message(message):
    print(message)

def make_result(success, msg, data=None):
    return {
        "success": success,
        "msg": msg,
        "data": data
    }

def get_active_habits_from_stats(result):
    return set(result["completed"]) | set(result["pending"])

def is_habit_active_on_date(info, selected_date):
    from validators import validate_date
    selected_date = validate_date(selected_date)

    created_at = validate_date(info["created_at"])

    archived_at = info.get("archived_at")
    archived_at = validate_date(archived_at) if archived_at else None

    return created_at <= selected_date and (archived_at is None or archived_at >= selected_date)

def count_logs_for_habit(data, habit):
    return sum(1 for log in data["logs"] if log["habit"] == habit)

def get_logged_habits_for_date(data, selected_date):
    selected_date = selected_date.isoformat()

    logged_habits = {log["habit"] for log in data["logs"] 
                    if log["date"] == selected_date}

    return sorted(logged_habits)