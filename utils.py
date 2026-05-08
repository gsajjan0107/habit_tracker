from datetime import datetime


def format_display_date(date_str):
    """
    Convert YYYY-MM-DD into a cleaner display format.
    Example:
    2026-05-08 -> 08 May 2026
    """

    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%d %b %Y")

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
    