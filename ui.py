from datetime import date
from stats import streak, longest_streak, times_done, repetitions


def show_habits(logs):
    for i, habit in enumerate(logs, start=1):
        print(f"{i} {habit.title()}")


def dashboard(logs):
    
    if not logs:
        print("No habits found.")
        return
    
    today = date.today().isoformat()
    
    for habit in logs:

        print()
        print("----------------------------------------------")
        print(habit.title())
        print()

        status = "Done" if today in logs[habit] else "Pending"
        print(f"{'Today\'s Status:':<25}{status:>5}")

        s = streak(habit, logs)
        l = longest_streak(habit, logs)

        print(f"{'Current Streak:':<25}{s:>5}")
        print(f"{'Longest Streak:':<25}{l:>5}")

        weekly = times_done(habit, 7, logs)
        weekly_pct = (weekly/7)*100

        monthly = times_done(habit, 30, logs)
        monthly_pct = (monthly/30)*100
        print(f"{'7-day consistency:':<25}{weekly_pct:>4.0f}%")
        print(f"{'30-day consistency:':<25}{monthly_pct:>4.0f}%")

        reps = repetitions(habit, logs)

        print(f"{'Total Reps:':<25}{reps:>5}")
        
    print()
    print("----------------------------------------------")