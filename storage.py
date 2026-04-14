from pathlib import Path
import json

FILE_PATH = Path(__file__).with_name("habits.json")


def load_habits():
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        logs = {habit: set(dates) for habit, dates in data.items()}
        return True, logs

    except (FileNotFoundError, json.JSONDecodeError):
        return False, {}


def save_habits(logs):
    try:
        serializable = {habit: sorted(dates) for habit, dates in logs.items()}

        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=4)

        return True, "Saved successfully."

    except Exception as e:
        return False, f"Failed to save habits: {e}"