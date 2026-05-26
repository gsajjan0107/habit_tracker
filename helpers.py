from datetime import datetime, date

def format_display_date(value):
    if isinstance(value, date):
        date_obj = value
    elif isinstance(value, str):
        date_obj = datetime.strptime(value, "%Y-%m-%d").date()
    else:
        raise ValueError("Date must be a string or date object.")

    return date_obj.strftime("%A, %d %B %Y")

def display_numbered_list(items):
    for i, item in enumerate(items, start=1):
        display_message(f"{i}. {item}")

def show_habits_status(result):
    pending = result["pending"]
    completed = result["completed"]

    if completed:
        habit_word = pluralize(len(completed), "habit")
        display_message(f"\n✅ Completed ({len(completed)} {habit_word}):")
        display_numbered_list(completed)

    if pending:
        habit_word = pluralize(len(pending), "habit")
        display_message(f"\n🚫 Unfinished ({len(pending)} {habit_word}):")
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

def pluralize(count, singular, plural=None):
    if plural is None:
        plural = singular + "s"

    return singular if count == 1 else plural

def format_weekly_message(info, status):
    day_word = pluralize(info["available_days_left"], "day")

    if info["status"] == "completed":
        return "✅ completed"

    if info["is_possible"]:
        return (
            f"{info['remaining']} more needed, "
            f"{info['available_days_left']} {day_word} available - {status}"
        )

    return (
        f"⚠️  Not possible this week "
        f"({info['remaining']} more needed, "
        f"{info['available_days_left']} {day_word} available)"
    )