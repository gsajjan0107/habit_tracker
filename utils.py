from validators import validate_int
from helpers import is_habit_archived, display_message
from storage import save_data

def get_selected_habits(pending):
    """Gets input for multiple habits and returns habit names."""
    while True:
        raw = input("\nEnter habit numbers, 'all', or 'q' to cancel: ").strip().lower()

        if not raw:
            display_message("Please select at least one habit, 'all', or 'q' to cancel.")
            continue

        if raw == 'q':
            return None

        if raw == "all":
            return pending[:]

        raw_choices = raw.split()

        # Remove Duplicates while preserving order
        habit_nums = []
        seen = set()
        for item in raw_choices:
            if item not in seen:
                habit_nums.append(item)
                seen.add(item)

        # Validate inputs
        selected_habits = []
        errors = []

        for habit_num in habit_nums:
            try:
                habit_num = validate_int(habit_num, 1, len(pending))
                habit_name = pending[habit_num - 1]
                selected_habits.append(habit_name)
            except ValueError as e:
                errors.append(str(e))

        if errors:
            for error in errors:
                display_message(f"Error: {error}")
            continue

        return selected_habits

def handle_operation_result(data, result):
    success = result.get("success", False)
    msg = result.get("msg", "Unknown operation result.")

    if success:
        save_data(data)

    display_message(msg)

def get_habit_from_habit_menu(data, cancel_message):
    """Gets input after showing habit menu. Returns habit name."""
    habits = sorted(data["habits"])

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

    for i, entry in enumerate(menu_entries, start=1):
        habit = entry["habit"]
        archived = entry["archived"]
        label = f"{habit} ({'archived' if archived else 'unarchived'})"
        display_message(f"{i}. {label}")

    while True:
        choice = input("\nSelect a habit number, or 'q' to cancel: ").strip().lower()

        if choice == "q":
            display_message(cancel_message)
            return None

        try:
            selected_index = validate_int(choice, 1, len(menu_entries))
            return menu_entries[selected_index - 1]["habit"]
        except ValueError as e:
            display_message(f"Error: {e}")