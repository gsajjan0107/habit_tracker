from datetime import datetime, date, timedelta
from config import DEFAULT_SCHEDULED_DAYS

def format_display_date(value):
    if isinstance(value, date):
        pass
    elif isinstance(value, str):
        value = datetime.strptime(value, "%Y-%m-%d").date()
    else:
        raise ValueError("Date must be a string or date object.")

    return value.strftime("%A, %d %B %Y")

def display_numbered_list(items):
    for i, item in enumerate(items, start=1):
        display_message(f"{i}. {item}")

def format_scheduled_days(scheduled_days) -> str:

    if scheduled_days == DEFAULT_SCHEDULED_DAYS:
        return "Everyday"
    elif scheduled_days == ["Mon", "Tue", "Wed", "Thu", "Fri"]:
        return "Weekdays"
    elif scheduled_days == ["Sat", "Sun"]:
        return "Weekends"
    else:
        return " ".join(scheduled_days)

def display_habit_list(data, habit_names):
    for index, habit_name in enumerate(habit_names, start=1):
        scheduled_days = data["habits"][habit_name]["scheduled_days"]
        schedule = format_scheduled_days(scheduled_days)
        display_message(f"{index}. {habit_name:<27}{schedule}")

def show_habits_status(data, result):
    pending = result["pending"]
    completed = result["completed"]

    if completed:
        habit_word = pluralize(len(completed), "habit")
        title = f"\n✅ Completed {habit_word}"
        display_message(f"{title:<30}Schedule")
        display_message("--------------------------------------------------")
        display_habit_list(data, completed)

    if pending:
        habit_word = pluralize(len(pending), "habit")
        title = f"\n🚫 Unfinished {habit_word}"
        display_message(f"{title:<30}Schedule")
        display_message("--------------------------------------------------")
        display_habit_list(data, pending)

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
    return data["habits"][habit_name].get("archived_at") is not None

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

def is_habit_active_on_date(habit_info, selected_date) -> bool:
    """Checks whether habit is active or archived."""

    from validators import validate_date
    from datetime import datetime, date

    if isinstance(selected_date, datetime):
        selected_date = selected_date.date()
    elif isinstance(selected_date, date):
        pass
    elif isinstance(selected_date, str):
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    else:
        raise ValueError("Date must be a string or date object.")

    created_at = validate_date(habit_info["created_at"])

    archived_at = habit_info.get("archived_at")
    archived_at = validate_date(archived_at) if archived_at else None

    return created_at <= selected_date and (archived_at is None or archived_at >= selected_date)

def pluralize(count, singular, plural=None):
    if plural is None:
        plural = singular + "s"

    return singular if count == 1 else plural

def format_weekly_message(info, status):
    day_word = pluralize(info["available_days_left"], "day")

    if info["status"] == "completed":
        return "✅  Target met"

    if info["is_possible"]:
        return (
            f"{info['remaining']} more needed, "
            f"{info['available_days_left']} {day_word} available - {status}")

    return (
        f"⚠️  Not possible this week "
        f"({info['remaining']} more needed, "
        f"{info['available_days_left']} {day_word} available)")

def format_weekly_status(status):
    status_labels = {
        "completed": "✅ completed",
        "in_progress": "🔄 in progress",
        "not_started": "⚪ not started",
    }

    return status_labels.get(status, status)

def get_previous_day_missed_habits(data, selected_date, daily_stats_func):
    previous_day = selected_date - timedelta(days=1)

    try:
        previous_day_result = daily_stats_func(data, previous_day)

        if previous_day_result["total_habits"] == 0:
            return previous_day, []

        return previous_day, sorted(previous_day_result["pending"])

    except ValueError:
        return previous_day, []


def habit_has_logs(data, habit_name):
    return any(log["habit"] == habit_name for log in data["logs"])

def get_habit_details(data, habit) -> dict:
    """Gives all details of the habit."""
    if habit not in data["habits"]:
        raise ValueError("Habit does not exist.")

    habit_data = data["habits"][habit]
    habit_logs = [log["date"] for log in data["logs"] if log["habit"] == habit]
    last_logged_at = max(habit_logs) if habit_logs else None
    total_logs = sum(1 for log in data["logs"] if log["habit"] == habit)

    return {
        "name": habit,
        "target_per_week": habit_data["target_per_week"],
        "scheduled_days": habit_data.get("scheduled_days", DEFAULT_SCHEDULED_DAYS.copy()),
        "created_at": habit_data["created_at"],
        "archived_at": habit_data["archived_at"],
        "is_archived": habit_data["archived_at"] is not None,
        "total_logs": total_logs,
        "last_logged_at": last_logged_at,
        "description": habit_data.get("description", ""),
    }

def get_today_focus_habits(pending_habits, weekly_stats):
    """Keeps the habits that still have unfinished weekly targets and sorts them by urgency."""
    focus_habits = []

    for habit in pending_habits:
        info = weekly_stats.get(habit)

        if info and info["remaining"] > 0:
            focus_habits.append((habit, info))

    focus_habits.sort(
        key=lambda item: (
            item[1]["available_days_left"],
            -item[1]["remaining"],
            item[0].lower()))

    return focus_habits

def is_habit_at_risk(info):
    return info["remaining"] > info["available_days_left"]

def display_weekly_progress_section(active_habits, weekly_stats, habit_streaks):
    habit_word = pluralize(len(active_habits), "habit")

    display_message(f"\n📊 Weekly Progress ({len(active_habits)} {habit_word}):")

    for habit in active_habits:
        info = weekly_stats[habit]
        streak_info = habit_streaks.get(habit, {"current_streak": 0, "longest_streak": 0})
        status = format_weekly_status(info["status"])
        weekly_message = format_weekly_message(info, status)
        display_message(f"\n{habit:<15}\nWeekly : {info['done']:>2}/{info['target']:<2} ({info['percentage']:.2f}%) - {weekly_message}\nStreak : 🔥 {streak_info['current_streak']}\nBest   : 🏆 {streak_info['longest_streak']}")

def get_most_neglected_habit(data, selected_date):
    from validators import validate_date

    most_neglected = None
    highest_days_since = -1

    for habit in data["habits"]:
        details = get_habit_details(data, habit)

        if details["is_archived"]:
            continue

        if details["last_logged_at"] is None:
            reference_date = validate_date(details["created_at"])
        else:
            reference_date = validate_date(details["last_logged_at"])

        days_since = (selected_date - reference_date).days

        if days_since > highest_days_since:
            highest_days_since = days_since
            most_neglected = habit

    if most_neglected is None:
        return None

    return most_neglected, highest_days_since

def get_best_performing_habit(weekly_stats):
    if not weekly_stats:
        return None

    habit_names = sorted(weekly_stats)

    best_habit = habit_names[0]
    best_percentage = weekly_stats[best_habit]["percentage"]

    for habit in habit_names[1:]:
        percentage = weekly_stats[habit]["percentage"]

        if percentage > best_percentage:
            best_habit = habit
            best_percentage = percentage

    return best_habit, best_percentage

def get_logs_for_date(data, selected_date):
    selected_date = selected_date.isoformat()

    logs = []

    for log in data["logs"]:
        if log["date"] == selected_date:
            logs.append({
                "habit": log["habit"],
                "note": log.get("note", "")
            })

    return sorted(logs, key=lambda log: log["habit"].lower())

def get_next_habit_id(data):
    habits = data["habits"]

    if not habits:
        return 1

    ids = []

    for habit in habits.values():
        ids.append(habit["id"])

    return max(ids) + 1

def get_scheduled_habits(data, date) -> set:
    """Gets habits that are active and scheduled for the date given."""

    weekday = date.strftime("%a")
    habits = data["habits"]
    valid_habits = set()

    for habit_name, habit_data in habits.items():
        if not is_habit_active_on_date(habit_data, date):
            continue

        if weekday in habit_data["scheduled_days"]:
            valid_habits.add(habit_name)

    return valid_habits

def get_scheduled_days():
    while True:
        display_message("Change schedule to:")
        display_message("1. Everyday (default)")
        display_message("2. Weekdays")
        display_message("3. Weekends")
        display_message("4. Custom")

        choice = input("\nEnter habit frequency (enter 'q' to cancel): ").strip().lower()

        if choice == "q":
            return None

        if choice == "":
            return DEFAULT_SCHEDULED_DAYS.copy()

        if choice in {"1", "2", "3", "4",}:

            if choice == "1":
                return DEFAULT_SCHEDULED_DAYS.copy()

            elif choice == "2":
                return DEFAULT_SCHEDULED_DAYS[:5]

            elif choice == "3":
                return DEFAULT_SCHEDULED_DAYS[-2:]

            elif choice == "4":

                while True:
                    for index, day in enumerate(DEFAULT_SCHEDULED_DAYS, start=1):
                        display_message(f"{index}. {day}")

                    raw = input("Enter day numbers separated by spaces. FYI 1 is Monday and 7 is Sunday.\n(e.g. 1 3 5, or 'q' to cancel): ").strip().lower()

                    if raw == "q":
                        return None

                    if raw == "":
                        display_message("Select at least one day.")
                        continue

                    choices = set(raw.split())

                    is_valid = True
                    valid_choices = {str(i) for i in range(1, 8)}
                    for i in choices:
                        if i not in valid_choices:
                            display_message("Invalid option. Enter numbers from 1-7.")
                            is_valid = False
                            break

                    if not is_valid:
                        continue

                    selected_days = {
                        DEFAULT_SCHEDULED_DAYS[int(i) - 1]
                        for i in choices
                    }

                    ordered_selected_days = [
                        day
                        for day in DEFAULT_SCHEDULED_DAYS
                        if day in selected_days
                    ]

                    if not get_confirmation(f"You have selected: {' '.join(ordered_selected_days)}. Confirm?: "):
                        continue

                    return ordered_selected_days

        else:
            display_message("Invalid option. Enter numbers from 1-4 or 'q' to cancel.")


