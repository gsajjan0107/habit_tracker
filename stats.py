from datetime import timedelta
from validators import validate_date
from helpers import is_habit_active_on_date

def logs_by_habit(data, date=None):
    logs = data["logs"]
    date = validate_date(date)

    habit_log_dates = {}
    for log in logs:
        
        habit_name = log.get("habit")
        if not habit_name:
            continue
        
        log_date = log.get("date")
        if not log_date:
            continue
        
        log_date = validate_date(log["date"])
    
        if log_date <= date:
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

    if not habits:
        raise ValueError("No habits created.")

    date = validate_date(date)
    habit_logs = logs_by_habit(data, date)

    result = {}

    for habit_name, habit_info in habits.items():
        if not is_habit_active_on_date(habit_info, date):
            continue

        log_dates = habit_logs.get(habit_name, set())

        result[habit_name] = {
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
    days_left = (sunday - date).days + 1

    habit_count = {}

    for log in data["logs"]:
        habit = log["habit"]
        log_date = validate_date(log["date"])

        if monday <= log_date <= sunday:
            habit_count[habit] = habit_count.get(habit, 0) + 1

    results = {}

    for name, info in habits.items():
        created_at = validate_date(info["created_at"])
        archived_at = info.get("archived_at")
        archived_at = validate_date(archived_at) if archived_at else None

        was_active_this_week = False

        for day in range(7):
            current_date = monday + timedelta(days=day)

            if is_habit_active_on_date(info, current_date):
                was_active_this_week = True
                break

        if not was_active_this_week:
            continue

        active_start = max(created_at, monday)
        active_end = min(archived_at, sunday) if archived_at else sunday
        active_days = (active_end - active_start).days + 1

        available_start = max(date, active_start)
        available_end = active_end

        available_days_left = 0
        if available_start <= available_end:
            available_days_left = (available_end - available_start).days + 1

        target = min(info["target_per_week"], active_days)
        done = habit_count.get(name, 0)
        remaining = max(target - done, 0)
        is_possible = remaining <= available_days_left

        percentage = 0
        if target > 0:
            percentage = round(min(done / target * 100, 100), 2)

        if done >= target:
            status = "completed"
        elif done > 0:
            status = "in_progress"
        else:
            status = "not_started"

        results[name] = {
            "done": done,
            "target": target,
            "remaining": remaining,
            "days_left": days_left,
            "available_days_left": available_days_left,
            "is_possible": is_possible,
            "percentage": percentage,
            "status": status
        }
        
    return results

def daily_stats(data, date=None):
    habits = data["habits"]

    if not habits:
        raise ValueError("No habits created.")

    date = validate_date(date)

    valid_habits = {name for name, info in habits.items()
        if is_habit_active_on_date(info, date)}

    if not valid_habits:
        return {
            "date": date.isoformat(),
            "completed": [],
            "pending": [],
            "total_completed": 0,
            "total_habits": 0,
            "completion_rate": 0
        }

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