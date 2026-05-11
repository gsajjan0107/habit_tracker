from validators import validate_int, validate_date
from helpers import is_habit_archived, display_message
from storage import save_data

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
                display_message(f"Error: {error}")
            continue
        
        return selected_habits

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

def format_habit_label(habit, archived):
    return f"{habit} ({'archived' if archived else 'unarchived'})"

def build_archive_menu_entries(data, habits):
    unarchived_habits = []
    archived_habits = []

    for habit in habits:
        archived = is_habit_archived(data, habit)
        if archived:
            archived_habits.append((habit, True))
        else:
            unarchived_habits.append((habit, False))
    
    unarchived_habits.sort(key=lambda item: item[0])
    archived_habits.sort(key=lambda item: item[0])

    all_habits = unarchived_habits + archived_habits
    return all_habits

def display_habit_archive_menu(data, habits):
    all_habits = build_archive_menu_entries(data, habits)

    for i, (habit, archived) in enumerate(all_habits, start=1):
        label = format_habit_label(habit, archived)
        display_message(f"{i}. {label}")

    return all_habits
    
def handle_operation_result(data, result):
    success = result.get("success", False)
    msg = result.get("msg", "Unknown operation result.")

    if success:
        save_data(data)

    display_message(msg)