from utils import parse_date
from datetime import datetime, timedelta

def get_habits_log_dates(data):
    logs = data["logs"]

    habit_log_dates = {}
    for log in logs:
        habit_name = log["habit"]
        log_date = parse_date(log["date"])
        
        habit_log_dates.setdefault(habit_name, set()).add(log_date)

    return habit_log_dates

def best_streak(log_dates):
    if not log_dates:
        return 0
    
    sorted_dates = sorted(log_dates)

    longest = current = 1

    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] == sorted_dates[i-1] + timedelta(days=1):
            current += 1
        else:
            longest = max(longest, current)
            current = 1

    return max(longest, current)

def current_streak(log_dates):
    if not log_dates:
        return 0
    
    streak = 0

    day = datetime.now().date()
    while day in log_dates:
        streak += 1
        day -= timedelta(days=1)

    return streak

def streaks(data):

    habit_logs = get_habits_log_dates(data)

    result = {}

    for habit in data["habits"]:
        log_dates = habit_logs.get(habit, set())

        max_streak = best_streak(log_dates)
        current = current_streak(log_dates)

        result[habit] = {
            "longest_streak": max_streak,
            "current_streak": current
        }

    return result

def habit_weekly_completion(data):
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    habit_count = {}

    logs = data["logs"]
    for log in logs:
        habit = log["habit"]
        date = parse_date(log["date"])

        if monday <= date <= sunday:
            habit_count[habit] = habit_count.get(habit, 0) + 1

    results = {}

    for name, info in data["habits"].items():
        if info.get("archived_at") is not None:
            continue
        
        target = info["target_per_week"]
        count = habit_count.get(name, 0)

        percentage = min((count / target) * 100, 100) if target > 0 else 0

        results[name] = {
            "done": count,
            "target": target,
            "percentage": percentage
        }

    return results

def weekly_stats_plus_streaks(data):
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    habit_count = {}

    logs = data["logs"]
    for log in logs:
        habit = log["habit"]
        date = parse_date(log["date"])

        if monday <= date <= sunday:
            habit_count[habit] = habit_count.get(habit, 0) + 1

    habit_logs = get_habits_log_dates(data)
    results = {}

    for name, info in data["habits"].items():
        if info.get("archived_at") is not None:
            continue
        
        target = info["target_per_week"]
        count = habit_count.get(name, 0)

        percentage = min((count / target) * 100, 100) if target > 0 else 0

        log_dates = habit_logs.get(name, set())
        max_streak = best_streak(log_dates)
        current = current_streak(log_dates)        

        results[name] = {
            "done": count,
            "target": target,
            "percentage": percentage,
            "longest_streak": max_streak,
            "current_streak": current
        }

    return results

def daily_stats(data, date=None):
    habits = data["habits"]

    if not habits:
        return False, "No habits created."

    if not date:
        date = datetime.now().date().isoformat()
    
    try:
        target_date = parse_date(date)
    except ValueError:
        return False, "Invalid date. Enter in (YYYY-MM-DD) format."

    valid_habits = {
        name for name, info in habits.items()
        if (parse_date(info["created_at"]) <= target_date) 
        and ((info.get("archived_at") is None) or (parse_date(info["archived_at"]) >= target_date))
    }

    completed_today = {
        log["habit"]
        for log in data["logs"]
        if log["date"] == date
    }

    completed = valid_habits & completed_today
    pending = valid_habits - completed

    return True, {
        "date": date,
        "completed": sorted(completed),
        "pending": sorted(pending),
        "total_completed": len(completed),
        "total_habits": len(valid_habits)
    }