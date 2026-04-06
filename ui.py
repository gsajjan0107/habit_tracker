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
        print(f"Today's Status:               {status}")

        s = streak(habit, logs)
        l = longest_streak(habit, logs)

        print(f"Current Streak:               {s}")
        print(f"Longest Streak:               {l}")

        weekly = times_done(habit, 7, logs)
        weekly_pct = (weekly/7)*100

        monthly = times_done(habit, 30, logs)
        monthly_pct = (monthly/30)*100

        print(f"7-day consistency:            {weekly_pct:.0f}%")
        print(f"30-day consistency:           {monthly_pct:.0f}%")

        reps = repetitions(habit, logs)

        print(f"Total Reps:                   {reps}")
        
    print()
    print("----------------------------------------------")