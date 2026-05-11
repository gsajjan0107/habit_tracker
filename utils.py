from datetime import datetime
from validators import validate_int, validate_date
from habits import log_habit

def format_display_date(date_str):
    """
    Convert YYYY-MM-DD into a cleaner display format.
    Example:
    2026-05-08 -> 08 May 2026
    """

    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%d %b %Y")

def get_selected_habits(pending):
    while True:
        raw = input("\nEnter habit numbers (or 'all'): ").strip().lower()

        if raw == 'q':
            return None

        if raw == "all":
            return pending[:]
    
        raw_choices = raw.split()

        # Remove Duplicates while preserving order
        choices = []
        seen = set()
        for item in raw_choices:
            if item not in seen:
                choices.append(item)
                seen.add(item)
            
        # Validate inputs
        selected_habits = []
        errors = []

        for choice in choices:
            try: 
                habit_num = validate_int(choice, 1, len(pending))
                habit_name = pending[habit_num - 1]
                selected_habits.append(habit_name)
            except ValueError as e:
                errors.append(str(e))

        if errors:
            for error in errors:
                print(f"Error: {error}")
            continue
        
        return selected_habits

def show_habits_status(result):
    formatted_date = format_display_date(result["date"])
    pending = result["pending"]
    completed = result["completed"]

    print(f"📅 Date: {formatted_date}")

    if pending:
        print("\n🚫 Pending:")
        display_numbered_list(pending)

    if completed:
        print("\n✅ Completed:")
        for habit in completed:
            print(f"- {habit}")

def filter_habits_by_creation_date(data, habits, log_date):
    valid_habits = []
    invalid_habits = []

    for habit in habits:
        created_date = data["habits"][habit]["created_at"]
        created_date = validate_date(created_date)

        if log_date < created_date:
            invalid_habits.append(habit)
        else:
            valid_habits.append(habit)

    return valid_habits, invalid_habits

def separate_logged_habits(valid_habits, completed):
    to_log = []
    skipped = []

    for habit in valid_habits:
        if habit in completed:
            skipped.append(habit)
        else:
            to_log.append(habit)

    return to_log, skipped

def log_multiple_habits(data, log_date, habits):
    logged = []
    for habit_name in habits:
        log_habit(data, log_date, habit_name)
        logged.append(habit_name)

    return logged

def get_confirmation(message):
    while True:
        confirm = input(message).strip().lower()

        if confirm in ["y", "yes"]:
            return True

        if confirm in ["n", "no"]:
            return False

        print("Invalid input. Please enter y/n.")

def get_today():
    return datetime.now().date()

def display_numbered_list(items):
    for i, item in enumerate(items, start=1):
        print(f"{i}. {item}")

def format_habit_status(habit, archived):
    status = "archived" if archived else "active"
    return f"{habit} ({status})"