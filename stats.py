from datetime import date, datetime, timedelta


def streak(habit, logs):
    
    today = date.today()

    if today.isoformat() not in logs[habit]:
        today -= timedelta(days=1)

    streak = 0
    days_set = set(logs[habit])
    
    while today.isoformat() in days_set:
        streak += 1
        today -= timedelta(days=1)
    
    return streak


def longest_streak(habit, logs):
    
    if not logs[habit]:
        return 0
    
    days_done = [
        datetime.strptime(d, "%Y-%m-%d").date()
        for d in logs[habit]
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
    
    today = date.today()

    if today.isoformat() not in logs[habit]:
        today -= timedelta(days=1)
        
    days_set = set(logs[habit])

    count = 0
    for _ in range(days):
        if today.isoformat() in days_set:
            count += 1
        today -= timedelta(days=1)
    
    return count

def repetitions(habit, logs):
    return len(logs[habit])