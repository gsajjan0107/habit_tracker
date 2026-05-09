import sys
from validators import *
from datetime import timedelta
from storage import load_data, save_data
from habits import *
from stats import daily_stats, habit_weekly_completion, streaks
from utils import *

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
        habit = get_valid_input(
            "Enter habit name: ",
            lambda v: validate_string(v, 3, 20)
            )

        existing_habit = data["habits"].get(habit)

        if existing_habit:
            
            if existing_habit.get("archived_at") is not None:
                print("Habit exists but is archived.")
            else:
                print("Habit already exists.")
            
            continue

        # VALIDATE TARGET
        target = get_valid_input(
            "Enter target per week: ",
            lambda v: validate_int(v, 1)
            )

        # ADD HABIT
        result = add_habit(data, habit, target)
        save_data(data)
        print(result)
        break

def handle_log(data):
    if not data["habits"]:
        print("No habits found. Add a habit first.")
        return
    
    while True: 
        try:
            log_date = input("\nEnter date (Press enter for today): ")
            log_date = validate_date(log_date)

            result = daily_stats(data, log_date)
            print()
            show_habits_status(result) # show pending and completed habits
            
            completed = result["completed"]
            pending = result["pending"]

            if not pending:
                print("\n🎉 All habits completed for this day!")
                return

            selected_habits = get_selected_habits(pending)

            # User enters 'q'
            if selected_habits is None:
                print("Logging cancelled.")
                return
            
            # Filter habits by creation date before logging
            valid_habits, invalid_habits = (
                filter_habits_by_creation_date(
                    data,
                    selected_habits,
                    log_date
                )
            )

            if invalid_habits:
                print("⚠️ Cannot log before creation date:")
                for habit in invalid_habits:
                    print(f"- {habit}")

            if not valid_habits:
                print("No valid habits to log.")
                continue
            
            # Check if already logged
            to_log, skipped = separate_logged_habits(
                valid_habits,
                completed
            )

            if skipped:
                print("⚠️ Already logged:")
                for habit_name in skipped:
                    print(f"- {habit_name}")

            if not to_log:
                print("Nothing new to log.")
                continue
            
            # Confirm logging
            print("\nYou are about to log:")
            for habit in to_log:
                print(f"- {habit}")

            confirm = input("\nProceed? (y/n): ").strip().lower()

            if confirm != 'y':
                print("Logging cancelled.")
                continue

            logged = log_multiple_habits(
                data,
                log_date,
                to_log
            )

            save_data(data)
            
            reset = []
            habit_streaks = streaks(data, log_date)
            
            print(f"\n✅ Logged {len(logged)} habits:")
            for habit in logged:
                current_habit_streak = habit_streaks[habit]["current_streak"]

                if current_habit_streak == 1:
                    print(f"\n⚠️ Streak reset: {habit} - 1 day streak")
                    reset.append(habit)
                else:
                    print(f"- {habit}: {current_habit_streak} days streak")

            break

        except ValueError as e:
            print(e)

def handle_delete_log(data):
    if not data["habits"]:
        print("No habits found. Add a habit first.")
        return
    
    if not data["logs"]:
        print("No logs found. Log a habit first.")
        return
    
    while True:
        try: # get valid date
            log_date = input("\nEnter date (Press enter for today): ")
            log_date = validate_date(log_date)
        except ValueError as e:
            print(e)
            continue

        result = daily_stats(data, log_date)
        formatted_date = format_display_date(result["date"])
        completed = result["completed"]

        if not completed:
            print("No logs for this date.")
            return
        
        print(f"\n📅 Date: {formatted_date}")
        print("\n✅ Logged:")
        for i, habit in enumerate(completed, start=1):
            print(f"{i}. {habit}")

        selected_habits = get_selected_habits(completed)

        if selected_habits is None:
            print("Log deletion cancelled.")
            return

        if not selected_habits:
            print("No habits selected.")
            continue

        break
    
    print("\nYou are about to delete logs for:")
    for habit in selected_habits:
        print(f"- {habit}")

    confirm = input("\nProceed? (y/n): ").strip().lower()

    if confirm != 'y':
        print("Log deletion cancelled.")
        return

    deleted = []
    for habit_name in selected_habits:
        result = delete_log(data, log_date, habit_name)
        if "deleted" in result.lower():
            deleted.append(habit_name)

    if not deleted:
        print("No logs were deleted.")
        return
        
    print(f"\n🗑️  Deleted {len(deleted)} logs:")
    for habit in deleted:
        print(f"- {habit}")

    save_data(data)

def handle_delete(data):
    if not data["habits"]:
        print("No habits found. Add a habit first.")
        return
    
    habits = [habit for habit in data["habits"]]
    for i, habit in enumerate(habits, start=1):
        print(f"{i}. {habit}")

    choice = get_valid_input(
        "\nSelect a habit (enter number): ",
        lambda n: validate_int(n, 1, len(habits)))
    
    habit = habits[choice - 1]

    if habit not in data["habits"]:
        raise ValueError("Habit does not exist.")
    
    confirm = get_valid_input(
        f"The habit [{habit}] will be deleted permanently along with logs. Confirm? (y/n): ",
        lambda v: validate_choice(v, ["y", "n"]))
    if confirm != "y":
        print("Deletion cancelled.")
        return
    
    # DELETE HABIT
    result = delete_habit(data, habit)
    save_data(data)
    print(result)
 
def handle_toggle_archive(data):
    if not data["habits"]:
        print("No habits found. Add a habit first.")
        return
    
    habits = [habit for habit in data["habits"]]

    for i, habit in enumerate(habits, start=1):
        if data["habits"][habit]["archived_at"] == None:
            print(f"{i}. {habit} (active)")
        else:
            print(f"{i}. {habit} (archived)")

    choice = get_valid_input(
        "\nSelect a habit (enter number): ",
        lambda n: validate_int(n, 1, len(habits)))
    
    habit = habits[choice - 1]
    habit_name = validate_string(habit, 3, 20)

    if habit_name not in data["habits"]:
        raise ValueError("Habit does not exist.")
    
    # TOGGLE ARCHIVE
    if data["habits"][habit].get("archived_at") is None:
        result = archive_habit(data, habit)
    else:
        result = unarchive_habit(data, habit)
    
    save_data(data)
    print(result)

def handle_dashboard(data):
    if not data["habits"]:
        print("No habits found. Add a habit first.")
        return
    
    while True:
        try:
            date = input("\nEnter date (Press enter for today): ")
            selected_date = validate_date(date)
            break
        except ValueError as e:
            print(e)
    
    previous_day = selected_date - timedelta(days=1)

    previous_day_result = daily_stats(data, previous_day)
    result = daily_stats(data, selected_date)

    print("\n==== DASHBOARD ====")
    show_habits_status(result)

    missed = previous_day_result["pending"]
    if missed:
        print("\n⚠️  Missed previous day:")
        for habit in missed:
            print(f"- {habit}")

    print(f"\nCompleted {result['total_completed']} / {result['total_habits']} ({result['completion_rate']:.2f}%) habits today.")

    print("\n📊 Weekly Stats:")

    weekly_stats = habit_weekly_completion(data, selected_date) # done, target, percentage
    habit_streaks = streaks(data, selected_date) # longest_streak, current_streak
    for habit, info in weekly_stats.items():
        # print(f"{habit:<15}:  {info['done']:>2}/{info['target']:<2} ({info['percentage']:.2f}%)   🔥 {habit_streaks[habit]['current_streak']} | 🎖️  {habit_streaks[habit]['longest_streak']}")
        print(f"\n{habit:<15}")
        print(f"  Weekly : {info['done']:>2}/{info['target']:<2} ({info['percentage']:.2f}%)")
        print(f"  Streak : 🔥 {habit_streaks[habit]['current_streak']}")
        print(f"  Best   : 🏆 {habit_streaks[habit]['longest_streak']}")

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
        print("\nMAIN MENU")
        print("--------------------")
        for key, label in commands.items():
            print(f"{key}. {label}")

        choice = get_valid_input(
            "\nEnter your choice: ",
            lambda v: validate_choice(v, [n for n in commands]))

        handlers[choice](data)

if __name__ == "__main__":
    main(data)