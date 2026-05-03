import sys
from validators import *
from pathlib import Path
from datetime import datetime, timedelta
from storage import load_data, save_data
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
    habit = get_valid_input("Enter habit name: ", lambda v: validate_string(v, 3, 20))

    if habit in data["habits"]:
        if data["habits"][habit].get("archived_at") is not None:
            raise ValueError("Habit exists but is archived.")
        else:
            raise ValueError("Habit already exists.")

    # VALIDATE TARGET
    target = get_valid_input("Enter target per week: ", lambda v: validate_int(v, 1))

    # ADD HABIT
    result = add_habit(data, habit, target)
    save_data(data)
    print(result)

def handle_log():
    while True:
        
        log_date = input("Enter date to log (Press enter for today): ")
        result = daily_stats(data, log_date)

        print("\n📅 Date:", result["date"])

        pending = result["pending"]
        if pending:
            print("\n🚫 Pending:")
            for i, habit in enumerate(pending, start=1):
                print(f"{i}. {habit}")
        else:
            print("\nNo habits to log.")
            return
        
        choices = set(input("\nEnter completed habit numbers: ").split())
        
        for choice in choices:
            choice = validate_int(choice, 1, len(pending))
            habit_name = pending[choice - 1]

            result = log_habit(data, habit_name, log_date)
            print(result)
        
        save_data(data)
        break

def handle_delete():
    if not data["habits"]:
        raise ValueError("No habits created.")
    
    habits = [habit for habit in data["habits"]]
    for i, habit in enumerate(habits, start=1):
        print(f"{i}. {habit}")

    choice = get_valid_input(
        "\nSelect a habit (enter number): ",
        lambda n: validate_int(n, 1, len(habits)))
    
    habit = habits[choice - 1]
    habit = validate_string(habit, 3, 20)

    if habit not in data["habits"]:
        raise ValueError("Habit does not exist.")
    
    confirm = get_valid_input(
        "The habit will be deleted permanently along with logs. Confirm? ",
        lambda v: validate_choice(v, ["y", "n"]))
    if confirm != "y":
        return
    
    # DELETE HABIT
    result = delete_habit(data, habit)
    save_data(data)
    print(result)
 
def handle_toggle_archive():
    if not data["habits"]:
        raise ValueError("No habits created.")
    
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
    habit_name = validate_string(habit_name, 3, 20)

    if habit_name not in data["habits"]:
        raise ValueError("Habit does not exist.")
    
    # TOGGLE ARCHIVE
    if data["habits"][habit].get("archived_at") is None:
        result = archive_habit(data, habit)
    else:
        result = unarchive_habit(data, habit)
    
    save_data(data)
    print(result)

def handle_dashboard():
    if not data["habits"]:
        raise ValueError("No habits created.")
    
    today = datetime.now().date()
    selected_date = input("Enter date to log (Press enter for today): ")
    
    if not selected_date:
        selected_date = today # Default
        yesterday = today - timedelta(days=1)
    else:
        selected_date = validate_date(selected_date) # Validate

    if selected_date > today:
        raise ValueError("Cannot show future data.")
    

    yesterday_result = daily_stats(data, yesterday)
    result = daily_stats(data, selected_date)

    print("\n==== DASHBOARD ====")
    print("📅 Date:", result["date"])

    completed = result["completed"]
    if completed:
        print("\n✅ Completed today:")
        for habit in result["completed"]:
            print(f"- {habit}")

    pending = result["pending"]
    if pending:
        print("\n🚫 Pending today:")
        for habit in pending:
            print(f"- {habit}")

    missed = yesterday_result["pending"]
    if missed:
        print("\n⚠️  Missed Yesterday:")
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

def main():
    while True:
        print("\nMAIN MENU")
        print("--------------------")
        for key, label in commands.items():
            print(f"{key}. {label}")

        choice = get_valid_input(
            "\nEnter your choice: ",
            lambda v: validate_choice(v, [n for n in commands]))

        handlers[choice]()

if __name__ == "__main__":
    main()