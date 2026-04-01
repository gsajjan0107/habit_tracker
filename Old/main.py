import json
from datetime import date

habits = ["Workout", "Meditation", "Python Practice"]

# Load existing logs
try:
    with open("log.json", "r") as f:
        logs = json.load(f)
except:
    logs = {}

today_log = {}

for habit in habits:
    answer = input(f"Did you complete {habit} today? (y/n): ")

    if answer == "y":
        today_log[habit] = True
    else:
        today_log[habit] = False

today = str(date.today())

logs[today] = today_log

with open("log.json", "w") as f:
    json.dump(logs, f, indent=4)

print("Progress saved.")