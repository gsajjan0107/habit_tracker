from datetime import date, datetime, timedelta


def streak(habit, logs):
    habit_logs = logs.get(habit, set())

    today = date.today()
    today_str = today.isoformat()

    if today_str not in habit_logs:
        today -= timedelta(days=1)
        today_str = today.isoformat()

    streak = 0
    
    while today_str in habit_logs:
        streak += 1
        today -= timedelta(days=1)
        today_str = today.isoformat()
    
    return streak


def longest_streak(habit, logs):
    habit_logs = logs.get(habit, set())
    
    if not logs[habit]:
        return 0
    
    days_done = [
        datetime.strptime(d, "%Y-%m-%d").date()
        for d in habit_logs
        ]
    
    days_done.sort()
    longest = current = 1

    for i in range(1, len(days_done)):

        if days_done[i] == days_done[i-1] + timedelta(days=1):
            current += 1
        else:
            longest = max(longest, current)
            current = 1
    
    return max(longest, current)


def times_done(habit, days, logs):
    habit_logs = logs.get(habit, set())

    today = date.today()
    today_str = today.isoformat()

    count = 0
    for _ in range(days):
        if today_str in habit_logs:
            count += 1
        today -= timedelta(days=1)
        today_str = today.isoformat()
    
    return count

def repetitions(habit, logs):
    return len(logs[habit])