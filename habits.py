from datetime import date
from storage import save_habits


def add_habit(habit, logs):
    habit = habit.lower().strip()
     
    if habit in logs:
        print(f"{habit.title()} already exists.")
        return
    
    logs[habit] = []
    save_habits(logs)
    print(f"{habit.title()} added.")

def delete_habit(habit, logs):

    if habit not in logs:
        print("Habit does not exist.")
        return
    
    del logs[habit]
    save_habits(logs)
    print(f"{habit.title()} deleted.")

def rename_habit(old, new, logs):
    new = new.lower().strip()

    if not new:
        print("Habit name cannot be empty.")
        return
    
    if new in logs:
        print(f"{new.title()} already exists.")
        return
    
    logs[new] = logs.pop(old)
    save_habits(logs)
    print(f"{old.title()} renamed to {new.title()}.")

def mark_habit_done(habit, logs):
    
    today = date.today().isoformat()
    
    if today in logs[habit]:
        print(f"{habit.title()} already marked today.")
    else:
        logs[habit].append(today)
        save_habits(logs)
        print(f"{habit.title()} marked done.")