import sys
from config import DEFAULT_SCHEDULED_DAYS
from storage import load_data, save_data
from stats import daily_stats, habit_weekly_completion, streaks
from validators import get_valid_input, validate_string, validate_int, validate_date, validate_choice
from habits import (
    add_habit,
    log_multiple_habits,
    delete_log,
    delete_habit,
    toggle_archive_habit,
    rename_habit,
    update_habit_target,
    get_habit_logs,
    update_habit_description,
    edit_habit_schedule)
from helpers import (
    show_habits_status,
    get_confirmation,
    format_display_date,
    display_numbered_list,
    habit_exists,
    is_habit_archived,
    ensure_habits_exist,
    display_message,
    pluralize,
    format_weekly_message,
    format_weekly_status,
    habit_has_logs,
    get_habit_details,
    display_weekly_progress_table,
    get_scheduled_days,
    format_scheduled_days,)

def get_selected_habits(pending):
    """Gets input as numbers for multiple habits and returns habit names."""
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

commands = {
    "1" : "Add habit",
    "2" : "Log habit",
    "3" : "Edit habit",
    "4" : "View habit details",
    "5" : "View logs",
    "6" : "Delete log",
    "7" : "Delete habit permanently",
    "8" : "Archive / Unarchive habit",
    "9" : "Dashboard",
    "10" : "Exit"
}

def handle_add(data):
    while True:
        habit_name = input("Enter habit name, or 'q' to cancel: ").strip()

        if habit_name.lower() == "q":
            display_message("Habit creation cancelled.")
            return

        try:
            habit_name = validate_string(habit_name, 3, 20)
        except ValueError as e:
            display_message(f"Error: {e}")
            continue

        if habit_exists(data, habit_name):

            if is_habit_archived(data, habit_name):
                display_message("Habit exists but is archived. Unarchive it instead.")
            else:
                display_message("Habit already exists.")

            continue

        while True:
            target_input = input("Enter target per week, or 'q' to cancel: ").strip()

            if target_input.lower() == "q":
                display_message("Habit creation cancelled.")
                return

            try:
                target = validate_int(target_input, 1)
                break
            except ValueError as e:
                display_message(f"Error: {e}")

        while True:
            scheduled_days = get_scheduled_days()

            if scheduled_days is None:
                display_message("Habit creation cancelled.")
                return

            if len(scheduled_days) < target:
                display_message("No. of scheduled days per week cannot be less than target.")
                continue

            break

        desc = input("Enter description / purpose (optional): ").strip()

        result = add_habit(data, habit_name, target, desc, scheduled_days)
        save_data(data)
        display_message(result)
        return

def handle_log(data):
    if not ensure_habits_exist(data):
        return

    while True:
        try:
            log_date = input("\nEnter date (Press enter for today, or 'q' to cancel): ").strip()

            if log_date.lower() == "q":
                display_message("Logging cancelled.")
                return

            log_date = validate_date(log_date)
            formatted_date = format_display_date(log_date)

            result = daily_stats(data, log_date)

            if result["total_habits"] == 0:
                display_message(f"No habits were active on {formatted_date}.")
                return

            show_habits_status(data, result) # Shows pending and completed habits list. Advice: Dont investigate here unless absolutely necessary. Nothing to do here.

            pending = result["pending"]
            if not pending:
                display_message(f"\n🎉 All habits completed for {formatted_date}!")
                return

            selected_habits = get_selected_habits(pending) # Gets number inputs and converts to habit names.

            # User enters 'q'
            if selected_habits is None:
                display_message("Logging cancelled.")
                return

            habit_word = pluralize(len(selected_habits), "habit")
            display_message(f"\nYou are about to log {len(selected_habits)} {habit_word} for {formatted_date}:")
            for habit in selected_habits:
                display_message(f"- {habit}")

            confirmed = get_confirmation("\nProceed? (y/n): ")
            if not confirmed:
                display_message("Logging cancelled.")
                return

            notes = {}
            for habit in selected_habits:
                note = input(f"Enter note for '{habit}' (optional): ").strip()
                notes[habit] = note

            logged = log_multiple_habits(data, log_date, selected_habits, notes)
            save_data(data)

            habit_streaks = streaks(data, log_date)

            habit_word = pluralize(len(logged), "habit")
            display_message(f"\n✅ Logged {len(logged)} {habit_word} for {formatted_date}:\n")

            for habit in logged:
                current_habit_streak = habit_streaks[habit]["current_streak"]
                day_word = pluralize(current_habit_streak, "day")
                display_message(f"- {habit}: {current_habit_streak} {day_word} streak")

            return

        except ValueError as e:
            display_message(e)

def handle_edit(data):
    if not ensure_habits_exist(data):
        return

    habit_name = get_habit_from_habit_menu(data, "Edit cancelled.") # display habit menu and get selected habit

    while True:
        display_message("\nEdit habit menu:\n")
        display_message("1. Rename habit")
        display_message("2. Change weekly target")
        display_message("3. Change scheduled days")
        display_message("4. Change description")
        display_message("Q. Return to main menu")

        choice = input("\nSelect a option number: ").strip().lower()

        if choice == "q":
            display_message("Returning to main menu.")
            return

        elif choice == "1":
            while True:
                try:
                    new_name = input("Enter new habit name: ").strip()
                    result = rename_habit(data, habit_name, new_name)
                    save_data(data)
                    display_message(result)
                    break
                except ValueError as e:
                    display_message(f"Error: {e}")

        elif choice == "2":
            while True:
                try:
                    new_target = input("Enter new weekly target: ").strip()
                    result = update_habit_target(data, habit_name, new_target)
                    save_data(data)
                    display_message(result)
                    break
                except ValueError as e:
                    display_message(f"Error: {e}")

        elif choice == "3":
            while True:
                current_schedule = format_scheduled_days(data["habits"][habit_name]["scheduled_days"])
                display_message(f"\n{habit_name}'s current schedule: {current_schedule}")

                scheduled_days = get_scheduled_days()

                if scheduled_days is None:
                    display_message("Edit cancelled.")
                    return

                try:
                    result = edit_habit_schedule(data, habit_name, scheduled_days,)
                    save_data(data)
                    display_message(result)
                    break
                except ValueError as e:
                    display_message(f"Error: {e}")

        elif choice == "4":
            while True:
                try:
                    desc = input("Enter new description: ").strip()
                    result = update_habit_description(data, habit_name, desc)
                    save_data(data)
                    display_message(result)
                    break
                except ValueError as e:
                    display_message(f"Error: {e}")

        else:
            display_message("Error: Invalid choice.")


# --- habit detail ---

def get_habit_detail_context(data, habit_name):
    details = get_habit_details(data, habit_name)
    archived_at = details["archived_at"]
    reference_date = (
        validate_date(archived_at)
        if archived_at is not None
        else validate_date("")
    )
    habit_streaks = streaks(data, reference_date)

    try:
        weekly_stats = habit_weekly_completion(data, reference_date) # Returns a dict with info of weekly performance of habits.
    except ValueError:
        weekly_stats = {}

    return details, reference_date, habit_streaks, weekly_stats

def display_habit_details_screen(
    habit,
    details,
    reference_date,
    habit_streaks,
    weekly_stats,
    ):

    habit_status = "Archived" if details["is_archived"] else "Active"
    streak_info = habit_streaks.get(habit, {})

    current_streak = streak_info.get("current_streak", 0)
    longest_streak = streak_info.get("longest_streak", 0)

    current_day_word = pluralize(current_streak, "day")
    best_day_word = pluralize(longest_streak, "day")

    schedule_display = format_scheduled_days(details.get("scheduled_days", DEFAULT_SCHEDULED_DAYS))

    created_at = format_display_date(details["created_at"])
    created_date = validate_date(details["created_at"])

    total_logs = details["total_logs"]
    habit_age = (reference_date - created_date).days
    habit_lifetime_days = habit_age + 1
    habit_lifetime_weeks = habit_lifetime_days / 7
    average_logs_per_week = total_logs / habit_lifetime_weeks
    consistency_percentage = total_logs / habit_lifetime_days * 100

    if consistency_percentage >= 90:
        rating = "Elite"
    elif consistency_percentage >= 75:
        rating = "Excellent"
    elif consistency_percentage >= 50:
        rating = "Good"
    elif consistency_percentage >= 25:
        rating = "Weak"
    else:
        rating = "Poor"

    habit_age_display = f"{habit_age} {pluralize(habit_age, "day")}"
    average_logs_display = f"{average_logs_per_week:.2f}"
    consistency_display = f"{consistency_percentage:.2f}% - {rating}"

    display_message("\n==== HABIT DETAILS ====\n")
    display_message(f"Habit: {details['name']}")
    if details["description"]:
        display_message(f"Description: {details['description']}")
    else:
        display_message("Description: No description provided")
    display_message(f"Target: {details['target_per_week']} per week")
    display_message(f"Schedule: {schedule_display}")
    display_message(f"Created: {created_at}")
    display_message(f"Habit age: {habit_age_display}")
    display_message(f"Status: {habit_status}")
    display_message(f"Total logs: {details['total_logs']}")
    display_message(f"Average logs per week: {average_logs_display}")
    display_message(f"Consistency: {consistency_display}")

    last_logged_at = details["last_logged_at"]
    if last_logged_at is None:
        display_message("Last logged: Never")
        display_message("Days since last log: N/A")
        return

    last_logged_date = validate_date(last_logged_at)
    days_since_last_log = (reference_date - last_logged_date).days
    day_word = pluralize(days_since_last_log, "day")
    days_since_last_log_display = f"{days_since_last_log} {day_word}"

    formatted_last_logged_at = format_display_date(last_logged_at)
    display_message(f"Last logged: {formatted_last_logged_at}")
    display_message(f"Days since last log: {days_since_last_log_display}")
    display_message(f"Current streak: {current_streak} {current_day_word}")
    display_message(f"Best streak: {longest_streak} {best_day_word}")

    if habit not in weekly_stats:
        return

    info = weekly_stats[habit]
    weekly_status = format_weekly_status(info["status"])
    weekly_message = format_weekly_message(info, weekly_status)

    display_message(f"This week: {info['done']}/{info['target']} completed ({info['percentage']:.2f}%) - {weekly_message}")
    display_message(f"Remaining this week: {info['remaining']}")

    if details["archived_at"] is None:
        return

    formatted_archived_at = format_display_date(details["archived_at"])
    display_message(f"Archived: {formatted_archived_at}")

def handle_view_habit_details(data):
    if not ensure_habits_exist(data):
        return

    habit_name = get_habit_from_habit_menu(data, "View habit details cancelled.") # display habit menu and get selected habit

    if habit_name is None:
        return

    try:
        details, reference_date, habit_streaks, weekly_stats = get_habit_detail_context(data, habit_name)
    except ValueError as e:
        display_message(e)
        return

    display_habit_details_screen(habit_name, details, reference_date, habit_streaks, weekly_stats)

def handle_view_logs(data):
    if not ensure_habits_exist(data):
        return

    display_message("1. Day logs")
    display_message("2. Habit logs")
    display_message("q. Cancel")

    while True:
        choice = input("\nSelect a option number, or 'q' to cancel: ").strip().lower()

        if choice == "q":
            display_message("View logs cancelled.")
            return

        elif choice == "1":
            while True:
                try:
                    date = input("\nEnter date (Press enter for today, or 'q' to cancel): ").strip()

                    if date.lower() == "q":
                        display_message("View logs cancelled.")
                        return

                    selected_date = validate_date(date)
                    result = daily_stats(data, selected_date)
                    completed = result["completed"]
                    pending = result["pending"]

                    logs = []

                    for log in data["logs"]:
                        if log["date"] == date:
                            logs.append({"habit": log["habit"], "note": log.get("note", "")})

                    day_logs = sorted(logs, key=lambda log: log["habit"].lower())

                    break

                except ValueError as e:
                    display_message(e)

            formatted_date = format_display_date(selected_date)

            display_message("\n==== VIEW LOGS ====")
            display_message(f"\n📅 Date: {formatted_date}")

            if result["total_habits"] == 0:
                display_message(f"No habits were active on {formatted_date}.")
                return

            if completed:
                display_message(f"\n✅ Logged habits ({len(completed)}):")

                for index, log in enumerate(day_logs, start=1):
                    message = f"{index}. {log['habit']}"

                    if log["note"]:
                        message += f" - {log['note']}"

                    display_message(message)
            else:
                display_message(f"\nNo habits logged on {formatted_date}.")

            if pending:
                display_message(f"\n🚫 Unfinished habits ({len(pending)}):")
                display_numbered_list(pending)
            else:
                display_message("\nAll active habits completed for this date.")

            return

        elif choice == "2":
            habit_name = get_habit_from_habit_menu(data, "Viewing cancelled.")
            result = get_habit_logs(data, habit_name)

            if not result:
                display_message("No logs for this habit yet.")
                return

            display_message(f"\n{habit_name} Logs")
            display_message("--------------------")
            for log in result:
                message = log["date"]

                if log["note"]:
                    message += f" - {log['note']}"

                display_message(message)

            return
        else:
            display_message("Error: Invalid choice.")

def handle_delete_log(data):
    if not ensure_habits_exist(data):
        return

    if not data["logs"]:
        display_message("No logs found yet. Log a habit first.")
        return

    while True:
        try:
            log_date = input("\nEnter date (Press enter for today, or 'q' to cancel): ").strip()

            if log_date.lower() == "q":
                display_message("Log deletion cancelled.")
                return

            log_date = validate_date(log_date)
            log_date_str = log_date.isoformat()
            completed = sorted({log["habit"] for log in data["logs"] if log["date"] == log_date_str})
            break

        except ValueError as e:
            display_message(e)

    formatted_date = format_display_date(log_date)

    if not completed:
        display_message(f"No logs found for {formatted_date}.")
        return

    display_message(f"\n📅 Date: {formatted_date}")
    display_message("\n✅ Logged:")
    display_numbered_list(completed)

    selected_habits = get_selected_habits(completed) # Gets number inputs and converts to habit names.

    if selected_habits is None:
        display_message("Log deletion cancelled.")
        return

    log_word = pluralize(len(selected_habits), "log")

    display_message(f"\nYou are about to delete {len(selected_habits)} {log_word} for {formatted_date}:")

    for habit in selected_habits:
        display_message(f"- {habit}")

    confirmed = get_confirmation("\nProceed? (y/n): ")

    if not confirmed:
        display_message("Log deletion cancelled.")
        return

    original_logs = data["logs"].copy()
    deleted = []

    try:
        for habit_name in selected_habits:
            result = delete_log(data, log_date, habit_name)
            if "deleted" in result.lower():
                deleted.append(habit_name)

    except ValueError as e:
        data["logs"] = original_logs
        display_message(e)
        return

    save_data(data)

    deleted_log_word = pluralize(len(deleted), "log")

    display_message(f"\n🗑️  Deleted {len(deleted)} {deleted_log_word} for {formatted_date}:")
    for habit in deleted:
        display_message(f"- {habit}")

def handle_delete(data):
    if not ensure_habits_exist(data):
        return

    habit = get_habit_from_habit_menu(data, "Deletion cancelled.")

    if habit is None:
        return

    if habit_has_logs(data, habit):
        display_message("Cannot permanently delete a habit with existing logs. Archive it instead.")
        return

    confirmed = get_confirmation(f"The habit [{habit}] will be deleted permanently. Confirm? (y/n): ")

    if not confirmed:
        display_message("Deletion cancelled.")
        return

    typed_name = input(f"Type the habit name [{habit}] to confirm permanent deletion: ").strip()

    if typed_name != habit:
        display_message("Habit name did not match. Deletion cancelled.")
        return

    try:
        result = delete_habit(data, habit)

    except ValueError as e:
        display_message(e)
        return

    save_data(data)
    display_message(result)

def handle_toggle_archive(data):
    if not ensure_habits_exist(data):
        return

    habit_name = get_habit_from_habit_menu(data, "Archive/unarchive cancelled.")

    if habit_name is None:
        return

    result = toggle_archive_habit(data, habit_name)
    success = result.get("success", False)
    msg = result.get("msg", "Unknown operation result.")

    if success:
        save_data(data)

    display_message(msg)

def handle_dashboard(data):
    if not ensure_habits_exist(data):
        return

    while True:
        try:
            date = input("\nEnter date (Press enter for today, or 'q' to cancel): ").strip()

            if date.lower() == "q":
                display_message("Dashboard cancelled.")
                return

            selected_date = validate_date(date)
            result: dict = daily_stats(data, selected_date)
            habit_streaks = streaks(data, selected_date)
            break

        except ValueError as e:
            display_message(e)

    display_message("\n==== DASHBOARD ====")
    formatted_date = format_display_date(result["date"])
    display_message(f"\n📅 {formatted_date}")

    active_habits = sorted(set(result["completed"]) | set(result["pending"]))
    display_weekly_progress_table(data, selected_date, active_habits, habit_streaks)

def handle_exit(data):
    sys.exit()

handlers = {
    "1": handle_add,
    "2": handle_log,
    "3": handle_edit,
    "4": handle_view_habit_details,
    "5": handle_view_logs,
    "6": handle_delete_log,
    "7": handle_delete,
    "8": handle_toggle_archive,
    "9": handle_dashboard,
    "10": handle_exit,
    }

def main(data):
    while True:
        display_message("\nMAIN MENU")
        display_message("--------------------")
        for key, label in commands.items():
            display_message(f"{key}. {label}")

        selected_index = get_valid_input(
            "\nEnter your choice: ",
            lambda v: validate_choice(v, [n for n in commands]))

        try:
            handlers[selected_index](data)
        except ValueError as e:
            display_message(e)

if __name__ == "__main__":
    data = load_data()
    main(data)