import sys
from validators import *
from pathlib import Path
from datetime import datetime
from storage import load_data, save_data
from utils import get_valid_habit_name, parse_date
from habits import add_habit, log_habit, delete_habit, archive_habit, unarchive_habit
from stats import daily_stats, habit_weekly_completion, streaks

file_path = Path(__file__).with_name("data.json")

commands = {
    "1" : "Add habit",
    "2" : "Log habit",
    "3" : "Delete habit",
    "4" : "Toggle archive",
    "5" : "Dashboard",
    "6" : "Exit"
}

data, result = load_data()

def handle_add():
    # VALIDATE HABIT
    habit = get_valid_input("Enter habit name: ", lambda v: validate_string(v, 3, 20))

    if habit in data["habits"]:
        if data["habits"][habit].get("archived_at") is not None:
            print("Habit exists but is archived.")
        else:
            print("Habit already exists.")
        return

    # VALIDATE TARGET
    target = get_valid_input("Enter target per week: ", lambda v: validate_int(v, 1))

    # ADD HABIT
    success, msg = add_habit(data, habit, target)
    save_data(data)
    print(msg)

def handle_log():
    # VALIDATE HABIT
    habit = get_valid_input("Enter habit name: ", lambda v: validate_string(v, 3, 20))

    if habit not in data["habits"]:
        print("Habit does not exist.")
        return

    if data["habits"][habit].get("archived_at") is not None:
        print("Cannot log as the habit is archived.")
        return
    
    # VALIDATE DATE
    log_date = input("Enter date (Press enter to log for today): ")
    
    if not log_date:
        log_date = datetime.now().date()
    else:
        log_date = get_valid_input(
            "Enter date (Press enter to log for today): ",
            validate_date
            )
        
    # LOG HABIT
    success, msg = log_habit(data, habit, log_date)
    save_data(data)
    print(msg)

def handle_delete():
    # VALIDATE HABIT
    habit = get_valid_input("Enter habit name: ", lambda v: validate_string(v, 3, 20))

    if habit not in data["habits"]:
        print("Habit does not exist.")
        return
    
    confirm = get_valid_input(
        "The habit will be deleted permanently along with logs. Confirm? ",
        lambda v: validate_choice(v, ["y", "n"]))
    if confirm != "y":
        return
    
    # DELETE HABIT
    success, msg = delete_habit(data, habit)
    save_data(data)
    print(msg)
 
def handle_toggle_archive():
    # VALIDATE HABIT
    habit = get_valid_input("Enter habit name: ", lambda v: validate_string(v, 3, 20))

    if habit not in data["habits"]:
        print("Habit does not exist.")
        return
    
    # TOGGLE ARCHIVE
    if data["habits"][habit].get("archived_at") is None:
        success, msg = archive_habit(data, habit)
    else:
        success, msg = unarchive_habit(data, habit)
    
    save_data(data)
    print(msg)

def handle_dashboard():
    success, result = daily_stats(data)
    if not success:
        print(result)
        return

    print("\n📅 Date:", result["date"])

    completed = result["completed"]
    if completed:
        print("\n✅ Completed:")
        for habit in result["completed"]:
            print(f"- {habit}")

    pending = result["pending"]
    if pending:
        print("\n🚫 Pending:")
        for habit in pending:
            print(f"- {habit}")

    print(f"\nCompleted {result['total_completed']} / {result['total_habits']} habits today.")

    print("\n📊 Weekly Stats:")
    
    weekly_stats = habit_weekly_completion(data) # done, target, percentage
    habit_streaks = streaks(data) # longest_streak, current_streak
    for habit, info in weekly_stats.items():
        print(f"{habit}:  {info['done']} / {info['target']} ({info['percentage']:.2f}%)   🔥 {habit_streaks[habit]['current_streak']} | 🎖️  {habit_streaks[habit]['longest_streak']}")

def handle_exit():
    sys.exit()
    
handlers = {
    "1": handle_add,
    "2": handle_log,
    "3": handle_delete,
    "4": handle_toggle_archive,
    "5": handle_dashboard,
    "6": handle_exit,
}

while True:
    print("\nMAIN MENU")
    print("--------------------")
    for key, label in commands.items():
        print(f"{key}. {label}")

    choice = get_valid_input(
        "\nEnter your choice: ",
        lambda v: validate_choice(v, [n for n in commands]))

    handlers[choice]()
