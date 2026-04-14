from datetime import date
from utils import get_sorted_habits
from stats import streak, longest_streak, times_done, repetitions


def format_habits(logs):
    lines = []
    for i, habit in enumerate(get_sorted_habits(logs), start=1):
        lines.append(f"{i}. {habit.title()}")
    return "\n".join(lines)


def format_dashboard(logs):
    if not logs:
        return "No habits found."
    
    output = []
    today = date.today().isoformat()

    for habit in get_sorted_habits(logs):
        output.append("\n----------------------------------------------\n")
        output.append(f"{habit.title()}\n")

        habit_logs = logs.get(habit, set())
        status = "Done" if today in habit_logs else "Pending"
        output.append(f"Today's Status: {status}")

        output.append(f"Current Streak: {streak(habit, logs)}")
        output.append(f"Longest Streak: {longest_streak(habit, logs)}")

        weekly = times_done(habit, 7, logs)
        monthly = times_done(habit, 30, logs)

        output.append(f"7-day consistency: {int((weekly/7)*100)}%")
        output.append(f"30-day consistency: {int((monthly/30)*100)}%")

        output.append(f"Total Reps: {repetitions(habit, logs)}")

    output.append("\n----------------------------------------------")
    return "\n".join(output)