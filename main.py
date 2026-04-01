import json
from datetime import date, datetime, timedelta

# Load
def load_habits(file_path="habits.json"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Could not load habits file. Starting fresh.")
        return {}

logs = load_habits()

# Save
def save_habits(logs, file_path="habits.json"):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)
    
# Add
def add_habit(habit, logs):
    habit = habit.lower().strip()
     
    if habit in logs:
        print(f"{habit.title()} already exists.")
    else:
        logs[habit] = []
        save_habits(logs)
        print(f"{habit.title()} added.")

# Convert habit number input to habit
def get_habit_dict(logs):
    return dict(enumerate(logs, start=1))

# Delete
def delete_habit(habit_num, logs):
    habit_dict = get_habit_dict(logs)
    habit = habit_dict.get(habit_num)
    
    if habit is None:
        print("Invalid habit number.")
        return
    
    del logs[habit]
    save_habits(logs)
    print(f"{habit.title()} deleted.")

# Rename
def rename_habit(habit_num, new_name, logs):
    habit_dict = get_habit_dict(logs)
    old_name = habit_dict.get(habit_num)
    
    if old_name is None:
        print("Invalid habit number.")
        return
    
    new_name = new_name.lower().strip()
    if new_name in logs:
        print(f"{new_name.title()} already exists.")
    else:
        logs[new_name] = logs.pop(old_name)
        save_habits(logs)
        print(f"{old_name.title()} renamed to {new_name.title()}.")

# Mark done
def mark_habit_done(habit_num, logs):
    habit_dict = get_habit_dict(logs)
    habit = habit_dict.get(habit_num)
    
    if habit is None:
        print("Invalid habit number.")
        return
    
    today = date.today().isoformat()
    
    if today in logs[habit]:
        print(f"{habit.title()} already marked as done.")
    else:
        logs[habit].append(today)
        save_habits(logs)
        print(f"{habit.title()} marked as done.")

# Streak
def streak(habit, logs):
    
    if habit is None:
        print("Invalid habit number.")
        return 0
    
    today = date.today()

    if today.isoformat() not in logs[habit]:
        today -= timedelta(days=1)

    streak = 0
    days_set = set(logs[habit])
    while True:
        day = today.isoformat()
        if day in days_set:
            streak += 1
            today -= timedelta(days=1)
        else:
            break
    
    return streak

# Longest streak
def longest_streak(habit, logs):
    
    if habit is None:
        print("Invalid habit number.")
        return 0

    if not logs[habit]:
        return 0
    
    days_done = [
        datetime.strptime(d, "%Y-%m-%d").date()
        for d in logs[habit]
        ]
    
    days_done.sort()
    longest = current = 1

    for i in range(1, len(days_done)):
        if days_done[i] == days_done[i-1] + timedelta(days=1):
            current += 1
        else:
            longest = max(longest, current)
            current = 1
    
    longest = max(longest, current)
    return longest

# Times habit done in given number of days
def times_done(habit, days, logs):
    
    if habit is None:
        print("Invalid habit number.")
        return 0
    
    today = date.today()
    days_set = set(logs[habit])

    count = 0
    for _ in range(days):
        day = today.isoformat()
        if day in days_set:
            count += 1
        today -= timedelta(days=1)
    
    return count

def repetitions(habit, logs):
    
    if habit is None:
        print("Invalid habit number.")
        return 0
    
    return len(logs[habit])

def show_habits(logs):
    
    if logs:
        habit_dict = get_habit_dict(logs)
        for k, v in habit_dict.items():
            print(f"{k} {v.title()}")
    else:
        print("No habits found. Add one first.")

def dashboard(logs):
    
    if not logs:
        print("No habits found. Add a habit first.")
        return
    
    today = date.today().isoformat()
    
    print()
    for habit in logs:

        print("----------------------------------------------")
        print()
        print(f"{habit.title()}:")

        status = "✔ Done" if today in logs[habit] else "✘ Pending"
        print(f"Today's Status: {status}")

        current_streak = streak(habit, logs)
        best_streak = longest_streak(habit, logs)
        print(f"Current Streak: {current_streak} | Longest Streak: {best_streak}")

        weekly_count = times_done(habit, 7, logs)
        weekly_percentage = (weekly_count/7)*100
        print(f"Consistency for 7 days: {weekly_percentage:.0f}%")

        monthly_count = times_done(habit, 30, logs)
        monthly_percentage = (monthly_count/30)*100
        print(f"Consistency for 30 days: {monthly_percentage:.0f}%")

        reps = repetitions(habit, logs)
        print(f"Total Reps: {reps}")
        print()
    print("----------------------------------------------")