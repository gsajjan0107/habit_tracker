import sys
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

data = load_data()

def handle_add():
    # VALIDATE HABIT
    success, result = get_valid_habit_name(input("Enter habit: "))
    if not success:
        print(result)
        return
    
    habit = result

    if habit in data["habits"]:
        if data["habits"][habit].get("archived_at") is not None:
            print("Habit exists but is archived.")
        else:
            print("Habit already exists.")
        return

    # VALIDATE TARGET
    try:
        target = int(input("Enter target per week: "))
        if target <= 0:
            print("Target must be at least 1.")
            return
    except ValueError:
        print("Target must be a valid number.")
        return

    # ADD HABIT
    success, msg = add_habit(data, habit, target)
    save_data(data)
    print(msg)

def handle_log():
    # VALIDATE HABIT
    success, result = get_valid_habit_name(input("Enter habit: "))
    if not success:
        print(result)
        return
    
    habit = result

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
        try:
            log_date = parse_date(log_date)
        except ValueError:
            print("Invalid date. Enter in (YYYY-MM-DD) format.")
            return

    # LOG HABIT
    success, msg = log_habit(data, habit, log_date)
    save_data(data)
    print(msg)

def handle_delete():
    # VALIDATE HABIT
    success, result = get_valid_habit_name(input("Enter habit: "))
    if not success:
        print(result)
        return
    
    habit = result

    if habit not in data["habits"]:
        print("Habit does not exist.")
        return
    
    confirm = input("The habit will be deleted permanently along with logs. Are you sure? (y/n): ").lower()
    if confirm != "y":
        return
    
    # DELETE HABIT
    success, msg = delete_habit(data, habit)
    save_data(data)
    print(msg)
 
def handle_toggle_archive():
    # VALIDATE HABIT
    success, result = get_valid_habit_name(input("Enter habit: "))
    if not success:
        print(result)
        return
    
    habit = result

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

    choice = input("\nEnter choice: ").strip()

    if choice not in handlers:
        print("Invalid choice.")
        continue

    handlers[choice]()
