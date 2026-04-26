def get_habit_exist_status(data, habit_name):
    
    if habit_name in data["habits"]:
        return True, "Habit exists."
    else:
        return False, "Habit does not exist."
    
def get_habit_archive_status(data, habit_name):
    if data["habits"][habit_name]["archived_at"] is not None:
        return True, "Habit is acrhived."
    else:
        return False, "Habit is not archived."
    