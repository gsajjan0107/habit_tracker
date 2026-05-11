from datetime import datetime

def format_display_date(date_str):
    """Convert YYYY-MM-DD into a cleaner display format: 2026-05-08 -> 08 May 2026"""

    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%d %b %Y")

def display_numbered_list(items):
    for i, item in enumerate(items, start=1):
        print(f"{i}. {item}")

def show_habits_status(result):
    formatted_date = format_display_date(result["date"])
    pending = result["pending"]
    completed = result["completed"]

    print(f"📅 Date: {formatted_date}")

    if pending:
        print("\n🚫 Pending:")
        display_numbered_list(pending)

    if completed:
        print("\n✅ Completed:")
        for habit in completed:
            print(f"- {habit}")

def get_confirmation(message):
    while True:
        confirm = input(message).strip().lower()

        if confirm in ["y", "yes"]:
            return True

        if confirm in ["n", "no"]:
            return False

        print("Invalid input. Please enter y/n.")

def get_today():
    return datetime.now().date()