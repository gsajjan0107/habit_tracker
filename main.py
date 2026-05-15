import sys
from validators import get_valid_input, validate_string, validate_int, validate_date, validate_choice
from datetime import timedelta
from storage import load_data, save_data
from habits import add_habit, log_multiple_habits, delete_log, delete_habit, toggle_archive_habit
from stats import daily_stats, habit_weekly_completion, streaks
from utils import get_selected_habits, filter_habits_by_creation_date, separate_logged_habits, display_habit_archive_menu, handle_operation_result
from helpers import show_habits_status, get_confirmation, format_display_date, display_numbered_list, habit_exists, is_habit_archived, ensure_habits_exist, display_message

commands = {
    "1" : "Add habit",
    "2" : "Log habit",
    "3" : "Delete Log",
    "4" : "Delete habit",
    "5" : "Toggle archive",
    "6" : "Dashboard",
    "7" : "Exit"
}

data = load_data()
 

def handle_add(data):
    while True:
        habit_name = get_valid_input("Enter habit name: ",
                lambda v: validate_string(v, 3, 20))

        if habit_exists(data, habit_name):
            
            if is_habit_archived(data, habit_name):
                display_message("Habit exists but is archived.")
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
            display_message("")
            show_habits_status(result) # show pending and completed habits
            
            completed = result["completed"]
            pending = result["pending"]

            if not pending:
                display_message("\n🎉 All habits completed for this day!")
                return


            selected_habits = get_selected_habits(pending)

            # User enters 'q'
            if selected_habits is None:
                display_message("Logging cancelled.")
                return
            

            # Filter habits by creation date before logging
            valid_habits, invalid_habits = (filter_habits_by_creation_date(data, selected_habits, log_date))

            if invalid_habits:
                display_message("⚠️  Cannot log before creation date:")
                for habit in invalid_habits:
                    display_message(f"- {habit}")

            if not valid_habits:
                display_message("No valid habits to log.")
                continue
            
            # Check if already logged
            to_log, skipped = separate_logged_habits(valid_habits, completed)

            if skipped:
                display_message("⚠️  Already logged:")
                for habit_name in skipped:
                    display_message(f"- {habit_name}")

            if not to_log:
                display_message("Nothing new to log.")
                continue
            
            # Confirm logging
            display_message("\nYou are about to log:")
            for habit in to_log:
                display_message(f"- {habit}")

            confirmed = get_confirmation("\nProceed? (y/n): ")

            if not confirmed:
                display_message("Logging cancelled.")
                continue

            logged = log_multiple_habits(data, log_date, to_log)
            save_data(data)
            
            reset = []
            habit_streaks = streaks(data, log_date)

            display_message(f"\n✅ Logged {len(logged)} habits:")
            for habit in logged:
                current_habit_streak = habit_streaks[habit]["current_streak"]

                if current_habit_streak == 1:
                    display_message(f"\n⚠️  Streak reset: {habit} - 1 day streak")
                    reset.append(habit)
                else:
                    display_message(f"- {habit}: {current_habit_streak} days streak")

            break

        except ValueError as e:
            display_message(e)

def handle_delete_log(data):
    if not ensure_habits_exist(data):
        return
    

    if not data["logs"]:
        display_message("No logs found. Log a habit first.")
        return
    

    while True:
        try: # get valid date
            log_date = input("\nEnter date (Press enter for today): ")
            log_date = validate_date(log_date)
        except ValueError as e:
            display_message(e)
            continue

        result = daily_stats(data, log_date)
        formatted_date = format_display_date(result["date"])
        completed = result["completed"]

        if not completed:
            display_message("No logs for this date.")
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
            continue

        break
    
    display_message("\nYou are about to delete logs for:")
    for habit in selected_habits:
        display_message(f"- {habit}")

    confirmed = get_confirmation("\nProceed? (y/n): ")

    if not confirmed:
        display_message("Log deletion cancelled.")
        return


    deleted = []
    for habit_name in selected_habits:
        result = delete_log(data, log_date, habit_name)
        if "deleted" in result.lower():
            deleted.append(habit_name)

    if not deleted:
        display_message("No logs were deleted.")
        return
        

    display_message(f"\n🗑️  Deleted {len(deleted)} logs:")
    for habit in deleted:
        display_message(f"- {habit}")

    save_data(data)

def handle_delete(data):
    if not ensure_habits_exist(data):
        return
    

    habits = list(data["habits"])
    display_numbered_list(habits)

    selected_index = get_valid_input("\nSelect a habit (enter number): ",
            lambda n: validate_int(n, 1, len(habits)))
    
    habit = habits[selected_index - 1]

    confirmed = get_confirmation(f"The habit [{habit}] will be deleted permanently along with logs. Confirm? (y/n): ")

    if not confirmed:
        display_message("Deletion cancelled.")
        return


    # DELETE HABIT
    result = delete_habit(data, habit)
    save_data(data)
    display_message(result)
 
def handle_toggle_archive(data):
    if not ensure_habits_exist(data):
        return
    

    habits = data["habits"]

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
            break

        except ValueError as e:
            display_message(e)
    
    result = daily_stats(data, selected_date)

    display_message("\n==== DASHBOARD ====")
    show_habits_status(result)

    previous_day = selected_date - timedelta(days=1)

    try:
        previous_day_result = daily_stats(data, previous_day)
        missed = previous_day_result["pending"]
    except ValueError:
        missed = []

    if missed:
        display_message("\n⚠️  Missed previous day:")
        for habit in missed:
            display_message(f"- {habit}")

    display_message(f"\nCompleted {result['total_completed']} / {result['total_habits']} ({result['completion_rate']:.2f}%) habits today.")

    display_message("\n📊 Weekly Stats:")

    weekly_stats = habit_weekly_completion(data, selected_date) # done, target, percentage
    habit_streaks = streaks(data, selected_date) # longest_streak, current_streak
    for habit, info in weekly_stats.items():
        display_message(f"\n{habit:<15}")
        display_message(f"  Weekly : {info['done']:>2}/{info['target']:<2} ({info['percentage']:.2f}%)")
        display_message(f"  Streak : 🔥 {habit_streaks[habit]['current_streak']}")
        display_message(f"  Best   : 🏆 {habit_streaks[habit]['longest_streak']}")

def handle_exit(data):
    sys.exit()
    
handlers = {
    "1": handle_add,
    "2": handle_log,
    "3": handle_delete_log,
    "4": handle_delete,
    "5": handle_toggle_archive,
    "6": handle_dashboard,
    "7": handle_exit,
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

        handlers[selected_index](data)

if __name__ == "__main__":
    main(data)