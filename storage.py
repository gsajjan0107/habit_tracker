from pathlib import Path
import json

FILE_PATH = Path(__file__).with_name("habits.json")


def load_habits():
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Could not load habits file. Starting fresh.")
        return {}


def save_habits(logs):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)