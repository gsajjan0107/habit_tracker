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

def format_habit_label(habit, archived):
    return f"{habit} ({'archived' if archived else 'unarchived'})"

def build_archive_menu_entries(data, habits):
    active_entries = []
    archived_entries = []

    for habit in habits:
        archived = is_habit_archived(data, habit)

        entry = {"habit": habit, "archived": archived}

        if archived:
            archived_entries.append(entry)
        else:
            active_entries.append(entry)

    active_entries.sort(key=lambda entry: entry["habit"])
    archived_entries.sort(key=lambda entry: entry["habit"])

    menu_entries = active_entries + archived_entries

    return menu_entries

def display_habit_archive_menu(data, habits):
    menu_entries = build_archive_menu_entries(data, habits)

    for i, entry in enumerate(menu_entries, start=1):
        habit = entry["habit"]
        archived = entry["archived"]
        label = format_habit_label(habit, archived)
        display_message(f"{i}. {label}")

    return menu_entries
    
def handle_operation_result(data, result):
    success = result.get("success", False)
    msg = result.get("msg", "Unknown operation result.")

    if success:
        save_data(data)

    display_message(msg)