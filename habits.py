from datetime import date


def add_habit(habit, logs):
    habit = habit.lower().strip()

    if not habit:
        return False, "Habit cannot be empty."
        
    if habit in logs:
        return False, f"{habit.title()} already exists."
    
    logs[habit] = set()
    return True, f"{habit.title()} added."


def delete_habit(habit, logs):

    if habit not in logs:
        return False, "Habit does not exist."
    
    del logs[habit]
    return True, f"{habit.title()} deleted."


def rename_habit(old, new, logs):
    new = new.lower().strip()

    if old not in logs:
        return False, "Habit does not exist."

    if not new:
        return False, "Habit name cannot be empty."
    
    if new in logs:
        return False, f"{new.title()} already exists."
    
    logs[new] = logs.pop(old)
    return True, f"{old.title()} renamed to {new.title()}."


def mark_habit_done(habit, logs):
    if habit not in logs:
        return False, "Habit does not exist."
    
    today = date.today().isoformat()
    
    if today in logs[habit]:
        return False, f"{habit.title()} already marked today."
    
    logs[habit].add(today)
    return True, f"{habit.title()} marked done."