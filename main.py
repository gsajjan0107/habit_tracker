import sys
from validators import get_valid_input, validate_string, validate_int, validate_date, validate_choice
from storage import load_data, save_data
from habits import add_habit, log_multiple_habits, delete_log, delete_habit, toggle_archive_habit, rename_habit, update_habit_target
from stats import daily_stats, habit_weekly_completion, streaks

from utils import (
    get_selected_habits,
    display_habit_archive_menu,
    handle_operation_result)

from helpers import (
    show_habits_status,
    get_confirmation,
    format_display_date,
    display_numbered_list,
    habit_exists,
    is_habit_archived,
    ensure_habits_exist,
    display_message,
    get_logged_habits_for_date,
    pluralize,
    format_weekly_message,
    format_weekly_status,
    format_daily_summary,
    get_sorted_active_habits_from_stats,
    format_log_confirmation_message,
    format_logged_success_message,
    format_streak_line,
    habit_has_logs,
    get_habit_details,
    get_today_focus_habits,
    display_today_focus_section,
    display_weekly_progress_section,
    get_dashboard_data,
    format_no_active_habits_message,
    get_previous_day_missed_habits,
    format_previous_day_missed_message,
    format_recovery_hint,
    display_completed_today_section,
    display_pending_today_section,
    get_habit_detail_metrics,
    get_days_since_last_log,
    get_habit_status_text,
    format_streak_display,
    format_habit_age,
    format_days_since_last_log,
    format_consistency_display,
    format_average_logs_per_week,
    )

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

        result = add_habit(data, habit_name, target)
        save_data(data)
        display_message(result)
        break

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

            result = daily_stats(data, log_date)
            pending = result["pending"]

            if result["total_habits"] == 0:
                formatted_date = format_display_date(log_date)
                display_message(format_no_active_habits_message(formatted_date))
                return


            show_habits_status(result) # show pending and completed habits

            if not pending:
                formatted_date = format_display_date(log_date)
                display_message(f"\n🎉 All habits completed for {formatted_date}!")
                return


            selected_habits = get_selected_habits(pending)

            # User enters 'q'
            if selected_habits is None:
                display_message("Logging cancelled.")
                return


            if not selected_habits:
                display_message("No habits selected.")
                return


            formatted_date = format_display_date(log_date)
            display_message(format_log_confirmation_message(selected_habits, formatted_date))

            for habit in selected_habits:
                display_message(f"- {habit}")

            confirmed = get_confirmation("\nProceed? (y/n): ")

            if not confirmed:
                display_message("Logging cancelled.")
                return


            logged = log_multiple_habits(data, log_date, selected_habits)
            save_data(data)

            habit_streaks = streaks(data, log_date)

            formatted_date = format_display_date(log_date)
            display_message(format_logged_success_message(logged, formatted_date))

            for habit in logged:
                current_habit_streak = habit_streaks[habit]["current_streak"]
                display_message(format_streak_line(habit, current_habit_streak))

            return

        except ValueError as e:
            display_message(e)

def handle_edit(data):
    if not ensure_habits_exist(data):
        return


    habits = sorted(data["habits"])
    menu_entries = display_habit_archive_menu(data, habits)

    while True:
        choice = input("\nSelect a habit number, or 'q' to cancel: ").strip().lower()

        if choice == "q":
            display_message("Edit cancelled.")
            return

        try:
            selected_index = validate_int(choice, 1, len(menu_entries))
            break
        except ValueError as e:
            display_message(f"Error: {e}")

    habit_name = menu_entries[selected_index - 1]["habit"]

    display_message("1. Rename habit")
    display_message("2. Change weekly target")
    display_message("Q. Cancel")

    while True:
        choice = input("\nSelect a option number, or 'q' to cancel: ").strip().lower()

        if choice == "q":
            display_message("Edit cancelled.")
            return

        elif choice == "1":
            new_name = input("Enter new habit name: ").strip()
            result = rename_habit(data, habit_name, new_name)
            save_data(data)
            display_message(result)
            break

        elif choice == "2":
            new_target = input("Enter new weekly target: ").strip()
            result = update_habit_target(data, habit_name, new_target)
            save_data(data)
            display_message(result)
            break

        else:
            display_message("Error: Invalid choice.")

# --- habit detail ---

def get_habit_detail_reference_date(archived_at):
    if archived_at is not None:
        return validate_date(archived_at)

    return validate_date("")

def display_last_logged_info(last_logged_at, selected_date):
    if last_logged_at is None:
        display_message("Last logged: Never")
        display_message("Days since last log: N/A")
        return

    last_logged_date = validate_date(last_logged_at)
    days_since_last_log = get_days_since_last_log(last_logged_date, selected_date)
    days_since_last_log_display = format_days_since_last_log(days_since_last_log)

    formatted_last_logged_at = format_display_date(last_logged_at)
    display_message(f"Last logged: {formatted_last_logged_at}")
    display_message(f"Days since last log: {days_since_last_log_display}")

def display_archived_info(archived_at):
    if archived_at is None:
        return

    formatted_archived_at = format_display_date(archived_at)
    display_message(f"Archived: {formatted_archived_at}")

def display_habit_weekly_info(habit, weekly_stats):
    if habit not in weekly_stats:
        return

    info = weekly_stats[habit]
    weekly_status = format_weekly_status(info["status"])
    weekly_message = format_weekly_message(info, weekly_status)

    display_message(
        f"This week: {info['done']}/{info['target']} "
        f"completed ({info['percentage']:.2f}%) - {weekly_message}"
    )

    display_message(f"Remaining this week: {info['remaining']}")

def display_habit_detail_summary(
    details,
    created_at,
    habit_age_display,
    habit_status,
    average_logs_display,
    consistency_display,
):
    display_message("\n==== HABIT DETAILS ====\n")
    display_message(f"Habit: {details['name']}")
    display_message(f"Target: {details['target_per_week']} per week")
    display_message(f"Created: {created_at}")
    display_message(f"Habit age: {habit_age_display}")
    display_message(f"Status: {habit_status}")
    display_message(f"Total logs: {details['total_logs']}")
    display_message(f"Average logs per week: {average_logs_display}")
    display_message(f"Consistency: {consistency_display}")

def display_streak_info(streak_display):
    display_message(f"Current streak: {streak_display['current_streak']}")
    display_message(f"Best streak: {streak_display['longest_streak']}")

def prepare_habit_detail_display_values(details, habit, habit_streaks, selected_date):
    habit_status = get_habit_status_text(details["is_archived"])
    streak_info = habit_streaks.get(habit, {"current_streak": 0, "longest_streak": 0})
    streak_display = format_streak_display(streak_info)

    created_at = format_display_date(details["created_at"])
    created_date = validate_date(details["created_at"])

    metrics = get_habit_detail_metrics(
        created_date,
        details["total_logs"],
        selected_date,
    )

    habit_age_display = format_habit_age(metrics["habit_age"])
    average_logs_display = format_average_logs_per_week(
        metrics["average_logs_per_week"]
    )
    consistency_display = format_consistency_display(
        metrics["consistency_percentage"],
        metrics["consistency_rating"],
    )

    return {
        "habit_status": habit_status,
        "streak_display": streak_display,
        "created_at": created_at,
        "habit_age_display": habit_age_display,
        "average_logs_display": average_logs_display,
        "consistency_display": consistency_display,
    }

def select_habit_from_archive_menu(data, cancel_message):
    habits = sorted(data["habits"])
    menu_entries = display_habit_archive_menu(data, habits)

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

def get_habit_detail_context(data, habit):
    details = get_habit_details(data, habit)
    selected_date = get_habit_detail_reference_date(details["archived_at"])
    habit_streaks = streaks(data, selected_date)

    try:
        weekly_stats = habit_weekly_completion(data, selected_date)
    except ValueError:
        weekly_stats = {}

    return details, selected_date, habit_streaks, weekly_stats

def display_habit_details_screen(
    habit,
    details,
    selected_date,
    weekly_stats,
    display_values,
):
    display_habit_detail_summary(
        details,
        display_values["created_at"],
        display_values["habit_age_display"],
        display_values["habit_status"],
        display_values["average_logs_display"],
        display_values["consistency_display"],
    )

    display_last_logged_info(details["last_logged_at"], selected_date)
    display_streak_info(display_values["streak_display"])
    display_habit_weekly_info(habit, weekly_stats)
    display_archived_info(details["archived_at"])

# Habit details flow:
# 1. Ensure at least one habit exists.
# 2. Let the user select an active or archived habit.
# 3. Load detail context:
#    - habit details
#    - reference date
#    - streaks
#    - weekly stats
# 4. Prepare formatted display values.
# 5. Render the habit details screen.
def handle_view_habit_details(data):
    if not ensure_habits_exist(data):
        return

    habit = select_habit_from_archive_menu(data, "View habit details cancelled.")

    if habit is None:
        return

    try:
        details, selected_date, habit_streaks, weekly_stats = get_habit_detail_context(
            data,
            habit,
        )
    except ValueError as e:
        display_message(e)
        return

    display_values = prepare_habit_detail_display_values(
        details,
        habit,
        habit_streaks,
        selected_date,
    )

    display_habit_details_screen(
        habit,
        details,
        selected_date,
        weekly_stats,
        display_values,
    )

def handle_view_logs(data):
    if not ensure_habits_exist(data):
        return

    while True:
        try:
            date = input("\nEnter date (Press enter for today, or 'q' to cancel): ").strip()

            if date.lower() == "q":
                display_message("View logs cancelled.")
                return

            selected_date = validate_date(date)
            result = daily_stats(data, selected_date)
            completed = sorted(result["completed"])
            pending = sorted(result["pending"])
            break

        except ValueError as e:
            display_message(e)

    formatted_date = format_display_date(selected_date)

    display_message("\n==== VIEW LOGS ====")
    display_message(f"\n📅 Date: {formatted_date}")

    if result["total_habits"] == 0:
        display_message(format_no_active_habits_message(formatted_date))
        return

    if completed:
        display_message(f"\n✅ Logged habits ({len(completed)}):")
        display_numbered_list(completed)
    else:
        display_message(f"\nNo habits logged on {formatted_date}.")

    if pending:
        display_message(f"\n🚫 Unfinished habits ({len(pending)}):")
        display_numbered_list(pending)
    else:
        display_message("\nAll active habits completed for this date.")

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
            completed = get_logged_habits_for_date(data, log_date)
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

    selected_habits = get_selected_habits(completed)

    if selected_habits is None:
        display_message("Log deletion cancelled.")
        return


    if not selected_habits:
        display_message("No habits selected.")
        return

    log_word = pluralize(len(selected_habits), "log")

    display_message(
        f"\nYou are about to delete {len(selected_habits)} {log_word} "
        f"for {formatted_date}:")

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

    if not deleted:
        display_message("No logs were deleted.")
        return

    save_data(data)

    deleted_log_word = pluralize(len(deleted), "log")

    display_message(
        f"\n🗑️  Deleted {len(deleted)} {deleted_log_word} "
        f"for {formatted_date}:")

    for habit in deleted:
        display_message(f"- {habit}")

def handle_delete(data):
    if not ensure_habits_exist(data):
        return


    habits = sorted(data["habits"])
    menu_entries = display_habit_archive_menu(data, habits)

    while True:
        choice = input("\nSelect a habit number, or 'q' to cancel: ").strip().lower()

        if choice == "q":
            display_message("Deletion cancelled.")
            return

        try:
            selected_index = validate_int(choice, 1, len(menu_entries))
            break
        except ValueError as e:
            display_message(f"Error: {e}")

    habit = menu_entries[selected_index - 1]["habit"]

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


    habits = sorted(data["habits"])

    menu_entries = display_habit_archive_menu(data, habits)

    while True:
        choice = input("\nSelect a habit number, or 'q' to cancel: ").strip().lower()

        if choice == "q":
            display_message("Archive/unarchive cancelled.")
            return

        try:
            selected_index = validate_int(choice, 1, len(menu_entries))
            break
        except ValueError as e:
            display_message(f"Error: {e}")

    entry = menu_entries[selected_index - 1]
    habit_name = entry["habit"]

    # TOGGLE ARCHIVE
    result = toggle_archive_habit(data, habit_name)
    handle_operation_result(data, result)

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

            dashboard_data = get_dashboard_data(data, selected_date)

            result = dashboard_data["daily"]
            weekly_stats = dashboard_data["weekly"]
            habit_streaks = dashboard_data["streaks"]

            break

        except ValueError as e:
            display_message(e)

    display_message("\n==== DASHBOARD ====")
    formatted_date = format_display_date(result["date"])
    display_message(f"\n📅 Date: {formatted_date}")

    if result["total_habits"] == 0:
        display_message(format_no_active_habits_message(formatted_date))
        return

    display_message("\n📌 Daily Summary")
    display_message(format_daily_summary(result, formatted_date))
    display_completed_today_section(result["completed"])
    display_pending_today_section(result["pending"])

    previous_day, missed = get_previous_day_missed_habits(data, selected_date, daily_stats)

    if missed:
        display_message("\n⚠️  Previous Day Missed")
        display_message(format_previous_day_missed_message(previous_day, missed))
        display_numbered_list(missed)
        display_message("")
        display_message(format_recovery_hint(missed))

    focus_habits = get_today_focus_habits(result["pending"], weekly_stats)

    display_today_focus_section(focus_habits)

    active_habits = get_sorted_active_habits_from_stats(result)
    display_weekly_progress_section(active_habits, weekly_stats, habit_streaks)

    display_message("\n✅ Dashboard loaded.")

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