import sys
from validators import get_valid_input, validate_string, validate_int, validate_date, validate_choice
from datetime import timedelta
from storage import load_data, save_data
from habits import add_habit, log_multiple_habits, delete_log, delete_habit, toggle_archive_habit
from stats import daily_stats, habit_weekly_completion, streaks

from utils import (
    get_selected_habits,
    display_habit_archive_menu,
    handle_operation_result
)

from helpers import (
    show_habits_status,
    get_confirmation,
    format_display_date,
    display_numbered_list,
    habit_exists,
    is_habit_archived,
    ensure_habits_exist,
    display_message,
    get_active_habits_from_stats,
    count_logs_for_habit,
    get_logged_habits_for_date,
    pluralize,
    format_weekly_message,
    format_weekly_status
)

commands = {
    "1" : "Add habit",
    "2" : "Log habit",
    "3" : "View logs",
    "4" : "Delete log",
    "5" : "Delete habit permanently",
    "6" : "Archive / Unarchive habit",
    "7" : "Dashboard",
    "8" : "Exit"
}

def handle_add(data):
    while True:
        habit_name = get_valid_input("Enter habit name: ",
                lambda v: validate_string(v, 3, 20))

        if habit_exists(data, habit_name):
            
            if is_habit_archived(data, habit_name):
                display_message("Habit exists but is archived. Unarchive it instead.")
            else:
                display_message("Habit already exists.")
            
            continue

        # VALIDATE TARGET
        target = get_valid_input("Enter target per week: ",
                lambda v: validate_int(v, 1))

        # ADD HABIT
        result = add_habit(data, habit_name, target)
        save_data(data)
        display_message(result)
        break

def handle_log(data):
    if not ensure_habits_exist(data):
        return
    
    while True: 
        try:
            log_date = input("\nEnter date (Press enter for today): ")
            log_date = validate_date(log_date)

            result = daily_stats(data, log_date)
            pending = result["pending"]

            if result["total_habits"] == 0:
                formatted_date = format_display_date(log_date)
                display_message(f"No habits were active on {formatted_date}.")
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
            
            # Confirm logging
            habit_word = pluralize(len(selected_habits), "habit")
            formatted_date = format_display_date(log_date)

            display_message(
                f"\nYou are about to log {len(selected_habits)} {habit_word} "
                f"for {formatted_date}:")

            for habit in selected_habits:
                display_message(f"- {habit}")

            confirmed = get_confirmation("\nProceed? (y/n): ")

            if not confirmed:
                display_message("Logging cancelled.")
                return

            logged = log_multiple_habits(data, log_date, selected_habits)
            save_data(data)
            
            habit_streaks = streaks(data, log_date)

            habit_word = pluralize(len(logged), "habit")
            formatted_date = format_display_date(log_date)

            display_message(
                f"\n✅ Logged {len(logged)} {habit_word} "
                f"for {formatted_date}:\n")

            for habit in logged:
                current_habit_streak = habit_streaks[habit]["current_streak"]
                day_word = pluralize(current_habit_streak, "day")

                display_message(f"- {habit}: {current_habit_streak} {day_word} streak")

            return

        except ValueError as e:
            display_message(e)

def handle_view_logs(data):
    if not ensure_habits_exist(data):
        return

    if not data["logs"]:
        display_message("No logs found yet. Log a habit first.")
        return

    while True:
        try:
            date = input("\nEnter date (Press enter for today): ")
            selected_date = validate_date(date)
            completed = get_logged_habits_for_date(data, selected_date)
            break

        except ValueError as e:
            display_message(e)

    formatted_date = format_display_date(selected_date)

    display_message("\n==== VIEW LOGS ====")
    display_message(f"\n📅 Date: {formatted_date}")

    if not completed:
        display_message(f"No habits logged on {formatted_date}.")
        return
    
    display_message(f"\n✅ Logged habits ({len(completed)}):")
    display_numbered_list(completed)

def handle_delete_log(data):
    if not ensure_habits_exist(data):
        return
    

    if not data["logs"]:
        display_message("No logs found yet. Log a habit first.")
        return
    

    while True:
        try:
            log_date = input("\nEnter date (Press enter for today): ")
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

    selected_index = get_valid_input("\nSelect a habit (enter number): ",
            lambda n: validate_int(n, 1, len(menu_entries)))
    
    habit = menu_entries[selected_index - 1]["habit"]
    log_count = count_logs_for_habit(data, habit)
    log_word = pluralize(log_count, "log")

    confirmed = get_confirmation(
        f"The habit [{habit}] will be deleted permanently along with "
        f"{log_count} {log_word}. Confirm? (y/n): ")

    if not confirmed:
        display_message("Deletion cancelled.")
        return
    

    typed_name = input(f"Type the habit name [{habit}] to confirm permanent deletion: ").strip()

    if typed_name != habit:
        display_message("Habit name did not match. Deletion cancelled.")
        return


    # DELETE HABIT
    result = delete_habit(data, habit)
    save_data(data)
    display_message(result)
 
def handle_toggle_archive(data):
    if not ensure_habits_exist(data):
        return
    

    habits = sorted(data["habits"])

    menu_entries = display_habit_archive_menu(data, habits)

    selected_index = get_valid_input("\nSelect a habit (enter number): ",
            lambda n: validate_int(n, 1, len(menu_entries)))
    
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
            date = input("\nEnter date (Press enter for today): ")
            selected_date = validate_date(date)
            result = daily_stats(data, selected_date)
            break

        except ValueError as e:
            display_message(e)
    
    display_message("\n==== DASHBOARD ====")
    formatted_date = format_display_date(result["date"])
    display_message(f"\n📅 Date: {formatted_date}")

    if result["total_habits"] == 0:
        display_message(f"No habits were active on {formatted_date}.")
        return

    show_habits_status(result)

    previous_day = selected_date - timedelta(days=1)

    try:
        previous_day_result = daily_stats(data, previous_day)
        if previous_day_result["total_habits"] == 0:
            missed = []
        else:
            missed = previous_day_result["pending"]

    except ValueError:
        missed = []

    if missed:
        previous_day_formatted = format_display_date(previous_day)
        habit_word = pluralize(len(missed), "habit")

        display_message(
            f"\n⚠️  Not logged on {previous_day_formatted} "
            f"({len(missed)} {habit_word}):")

        display_numbered_list(missed)

    habit_word = pluralize(result["total_habits"], "habit")

    display_message(
        f"\nDaily Summary: {result['total_completed']}/{result['total_habits']} "
        f"{habit_word} completed ({result['completion_rate']:.2f}%) "
        f"on {formatted_date}.")

    active_habits = get_active_habits_from_stats(result)
    habit_word = pluralize(len(active_habits), "habit")

    display_message(f"\n📊 Weekly Progress ({len(active_habits)} {habit_word}):")

    weekly_stats = habit_weekly_completion(data, selected_date)
    habit_streaks = streaks(data, selected_date)

    status_labels = {
        "completed": "✅ completed",
        "in_progress": "🔄 in progress",
        "not_started": "⚪ not started",
    }

    for habit, info in weekly_stats.items():
        if habit not in active_habits:
            continue

        streak_info = habit_streaks.get(habit, {"current_streak": 0, "longest_streak": 0})
        status = format_weekly_status(info["status"])
        weekly_message = format_weekly_message(info, status)

        display_message(f"\n{habit:<15}")
        display_message(
            f"  Weekly : {info['done']:>2}/{info['target']:<2} "
            f"({info['percentage']:.2f}%) - {weekly_message}")
        display_message(f"  Streak : 🔥 {streak_info['current_streak']}")
        display_message(f"  Best   : 🏆 {streak_info['longest_streak']}")

def handle_exit(data):
    sys.exit()
    
handlers = {
    "1": handle_add,
    "2": handle_log,
    "3": handle_view_logs,
    "4": handle_delete_log,
    "5": handle_delete,
    "6": handle_toggle_archive,
    "7": handle_dashboard,
    "8": handle_exit,
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