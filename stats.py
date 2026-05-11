from datetime import timedelta
from validators import *

def logs_by_habit(data, date=None):
    logs = data["logs"]

    habit_log_dates = {}
    for log in logs:
        
        habit_name = log.get("habit")
        if not habit_name:
            continue
        
        log_date = log.get("date")
        if not log_date:
            continue
        
        log_date = validate_date(log["date"])
    
        if log_date <= date: # type: ignore
            habit_log_dates.setdefault(habit_name, set()).add(log_date)

    return habit_log_dates

def best_streak(log_dates):
    if not log_dates:
        return 0

    sorted_dates = sorted(set(log_dates))

    longest = current = 1

    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] == sorted_dates[i - 1] + timedelta(days=1):
            current += 1
        else:
            longest = max(longest, current)
            current = 1

    return max(longest, current)

def current_streak(log_dates, end_date):
    if not log_dates:
        return 0

    streak = 0
    day = end_date

    while day in log_dates:
        streak += 1
        day -= timedelta(days=1)

    return streak

def streaks(data, date=None):
    habits = data["habits"]
    logs = data["logs"]

    if not habits:
        raise ValueError("No habits created.")
    
    if not logs:
        raise ValueError("No logs found.")
    
    habit_logs = logs_by_habit(data, date)

    result = {}

    for habit in habits:
        log_dates = habit_logs.get(habit, set())

        result[habit] = {
            "longest_streak": best_streak(log_dates),
            "current_streak": current_streak(log_dates, date)
        }

    return result

def habit_weekly_completion(data, date=None):
    habits = data["habits"]

    if not habits:
        raise ValueError("No habits created.")

    date = validate_date(date)

    monday = date - timedelta(days=date.weekday())
    sunday = monday + timedelta(days=6)

    habit_count = {}

    for log in data["logs"]:
        habit = log["habit"]
        log_date = validate_date(log["date"])

        if monday <= log_date <= sunday:
            habit_count[habit] = habit_count.get(habit, 0) + 1

    results = {}

    for name, info in habits.items():
        created_at = validate_date(info["created_at"])

        if created_at > sunday:
            continue

        archived_at = info.get("archived_at")
        if archived_at:
            archived_at = validate_date(archived_at)
            if archived_at < monday:
                continue

        target = info["target_per_week"]
        done = habit_count.get(name, 0)

        percentage = 0
        if target > 0:
            percentage = round(min(done / target * 100, 100), 2)

        results[name] = {
            "done": done,
            "target": target,
            "percentage": percentage
        }

    return results

def daily_stats(data, date=None):
    habits = data["habits"]

    if not habits:
        raise ValueError("No habits created.")

    date = validate_date(date)

    valid_habits = set()

    for habit_name, habit_info in habits.items():
        habit_created_at = validate_date(habit_info["created_at"])
        habit_archived_at = habit_info.get("archived_at")

        if habit_archived_at:
            habit_archived_at = validate_date(habit_archived_at)

        if habit_created_at <= date and (habit_archived_at is None or habit_archived_at >= date):
            valid_habits.add(habit_name)

    if not valid_habits:
        raise ValueError(f"No valid habits for {date.isoformat()}")

    completed_on_date = {
        log["habit"]
        for log in data["logs"]
        if log["date"] == date.isoformat()
    }

    completed = valid_habits & completed_on_date
    pending = valid_habits - completed

    total = len(valid_habits)

    return {
        "date": date.isoformat(),
        "completed": sorted(completed),
        "pending": sorted(pending),
        "total_completed": len(completed),
        "total_habits": total,
        "completion_rate": round(len(completed) / total * 100, 2)
    }