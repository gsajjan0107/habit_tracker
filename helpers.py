from datetime import datetime, date, timedelta

TODAYS_FOCUS_ON_TRACK_MESSAGE = (
    "All weekly targets are currently on track. "
    "Choose any pending habit or recover."
)

def format_display_date(value):
    if isinstance(value, date):
        date_obj = value
    elif isinstance(value, str):
        date_obj = datetime.strptime(value, "%Y-%m-%d").date()
    else:
        raise ValueError("Date must be a string or date object.")

    return date_obj.strftime("%A, %d %B %Y")

def display_numbered_list(items):
    for i, item in enumerate(items, start=1):
        display_message(f"{i}. {item}")

def show_habits_status(result):
    pending = sorted(result["pending"])
    completed = sorted(result["completed"])

    if completed:
        habit_word = pluralize(len(completed), "habit")
        display_message(f"\n✅ Completed ({len(completed)} {habit_word}):")
        display_numbered_list(completed)

    if pending:
        habit_word = pluralize(len(pending), "habit")
        display_message(f"\n🚫 Unfinished ({len(pending)} {habit_word}):")
        display_numbered_list(pending)

def get_confirmation(message):
    while True:
        confirm = input(message).strip().lower()

        if confirm in ["y", "yes"]:
            return True

        if confirm in ["n", "no"]:
            return False

        display_message("Please enter y/yes or n/no.")

def get_today():
    return datetime.now().date()

def habit_exists(data, habit_name):
    return data["habits"].get(habit_name)

def is_habit_archived(data, habit_name):
    return (data["habits"][habit_name].get("archived_at") is not None)

def ensure_habits_exist(data):
    if not data["habits"]:
        display_message("No habits found. Add a habit first.")
        return False

    return True

def display_message(message):
    print(message)

def make_result(success, msg, data=None):
    return {
        "success": success,
        "msg": msg,
        "data": data
    }

def get_active_habits_from_stats(result):
    return set(result["completed"]) | set(result["pending"])

def is_habit_active_on_date(info, selected_date):
    from validators import validate_date
    from datetime import datetime, date

    if isinstance(selected_date, datetime):
        selected_date = selected_date.date()
    elif isinstance(selected_date, date):
        pass
    elif isinstance(selected_date, str):
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    else:
        raise ValueError("Date must be a string or date object.")

    created_at = validate_date(info["created_at"])

    archived_at = info.get("archived_at")
    archived_at = validate_date(archived_at) if archived_at else None

    return created_at <= selected_date and (archived_at is None or archived_at >= selected_date)

def count_logs_for_habit(data, habit):
    return sum(1 for log in data["logs"] if log["habit"] == habit)

def get_logged_habits_for_date(data, selected_date):
    selected_date = selected_date.isoformat()

    logged_habits = {log["habit"] for log in data["logs"]
                    if log["date"] == selected_date}

    return sorted(logged_habits)

def pluralize(count, singular, plural=None):
    if plural is None:
        plural = singular + "s"

    return singular if count == 1 else plural

def format_weekly_message(info, status):
    day_word = pluralize(info["available_days_left"], "day")

    if info["status"] == "completed":
        return "✅  Target met"

    if info["is_possible"]:
        return (
            f"{info['remaining']} more needed, "
            f"{info['available_days_left']} {day_word} available - {status}")

    return (
        f"⚠️  Not possible this week "
        f"({info['remaining']} more needed, "
        f"{info['available_days_left']} {day_word} available)")

def format_weekly_status(status):
    status_labels = {
        "completed": "✅ completed",
        "in_progress": "🔄 in progress",
        "not_started": "⚪ not started",
    }

    return status_labels.get(status, status)

def format_daily_summary(result, formatted_date):
    habit_word = pluralize(result["total_habits"], "habit")

    return (
        f"{result['total_completed']}/{result['total_habits']} "
        f"{habit_word} completed ({result['completion_rate']:.2f}%) "
        f"on {formatted_date}."
    )

def format_previous_day_missed_message(previous_day, missed):
    previous_day_formatted = format_display_date(previous_day)
    habit_word = pluralize(len(missed), "habit")

    return (
        f"Not logged on {previous_day_formatted} "
        f"({len(missed)} {habit_word}):"
    )

def get_sorted_active_habits_from_stats(result):
    return sorted(get_active_habits_from_stats(result))

def get_previous_day_missed_habits(data, selected_date, daily_stats_func):
    previous_day = selected_date - timedelta(days=1)

    try:
        previous_day_result = daily_stats_func(data, previous_day)

        if previous_day_result["total_habits"] == 0:
            return previous_day, []

        return previous_day, sorted(previous_day_result["pending"])

    except ValueError:
        return previous_day, []

def format_log_confirmation_message(selected_habits, formatted_date):
    habit_word = pluralize(len(selected_habits), "habit")

    return (
        f"\nYou are about to log {len(selected_habits)} {habit_word} "
        f"for {formatted_date}:"
    )

def format_logged_success_message(logged, formatted_date):
    habit_word = pluralize(len(logged), "habit")

    return (
        f"\n✅ Logged {len(logged)} {habit_word} "
        f"for {formatted_date}:\n"
    )

def format_streak_line(habit, current_streak):
    day_word = pluralize(current_streak, "day")

    return f"- {habit}: {current_streak} {day_word} streak"

def habit_has_logs(data, habit):
    return any(log["habit"] == habit for log in data["logs"])

def get_habit_details(data, habit):
    if habit not in data["habits"]:
        raise ValueError("Habit does not exist.")

    habit_data = data["habits"][habit]
    habit_logs = [
        log["date"]
        for log in data["logs"]
        if log["habit"] == habit
    ]

    last_logged_at = max(habit_logs) if habit_logs else None

    return {
        "name": habit,
        "target_per_week": habit_data["target_per_week"],
        "created_at": habit_data["created_at"],
        "archived_at": habit_data["archived_at"],
        "is_archived": habit_data["archived_at"] is not None,
        "total_logs": count_logs_for_habit(data, habit),
        "last_logged_at": last_logged_at,
        "description": habit_data.get("description", ""),
    }

def get_today_focus_habits(pending_habits, weekly_stats):
    focus_habits = []

    for habit in pending_habits:
        info = weekly_stats.get(habit)

        if info and info["remaining"] > 0:
            focus_habits.append((habit, info))

    focus_habits.sort(
        key=lambda item: (
            item[1]["available_days_left"],
            -item[1]["remaining"],
            item[0].lower(),
        )
    )

    return focus_habits

def is_habit_at_risk(info):
    return info["remaining"] > info["available_days_left"]

def format_today_focus_message(habit, info):
    day_word = pluralize(info["available_days_left"], "day")
    risk_note = ""

    if is_habit_at_risk(info):
        risk_note = " ⚠️  At risk"

    return (
        f"- {habit}: {info['remaining']} more needed this week, "
        f"{info['available_days_left']} {day_word} available"
        f"{risk_note}"
    )

def format_weekly_progress_lines(habit, info, streak_info):
    status = format_weekly_status(info["status"])
    weekly_message = format_weekly_message(info, status)

    return [
        f"\n{habit:<15}",
        (
            f"  Weekly : {info['done']:>2}/{info['target']:<2} "
            f"({info['percentage']:.2f}%) - {weekly_message}"
        ),
        f"  Streak : 🔥 {streak_info['current_streak']}",
        f"  Best   : 🏆 {streak_info['longest_streak']}",
    ]

def display_today_focus_section(focus_habits):
    display_message("\n🎯 Today's Focus")

    if focus_habits:
        for habit, info in focus_habits:
            display_message(format_today_focus_message(habit, info))
    else:
        display_message(TODAYS_FOCUS_ON_TRACK_MESSAGE)

def display_weekly_progress_section(active_habits, weekly_stats, habit_streaks):
    habit_word = pluralize(len(active_habits), "habit")

    display_message(f"\n📊 Weekly Progress ({len(active_habits)} {habit_word}):")

    for habit in active_habits:
        info = weekly_stats[habit]
        streak_info = habit_streaks.get(
            habit,
            {"current_streak": 0, "longest_streak": 0},
        )

        for line in format_weekly_progress_lines(habit, info, streak_info):
            display_message(line)

def get_dashboard_data(data, selected_date):
    from stats import daily_stats, habit_weekly_completion, streaks

    return {
        "daily": daily_stats(data, selected_date),
        "weekly": habit_weekly_completion(data, selected_date),
        "streaks": streaks(data, selected_date),
    }

def format_no_active_habits_message(formatted_date):
    return f"No habits were active on {formatted_date}."

def format_recovery_hint(missed):
    if not missed:
        return ""

    habit_word = pluralize(len(missed), "habit")
    pronoun = "them" if len(missed) > 1 else "it"

    return (
        f"Recovery hint: Pick the easiest missed {habit_word} "
        f"and complete {pronoun} first today."
    )

def display_completed_today_section(completed_habits):
    display_message("\n✅ Completed Today")

    if completed_habits:
        display_numbered_list(completed_habits)
    else:
        display_message("No habits completed yet today.")

def display_pending_today_section(pending_habits):
    display_message("\n⏳ Pending Today")

    if pending_habits:
        display_numbered_list(pending_habits)
    else:
        display_message("All active habits completed for today.")

def get_consistency_rating(percentage):
    if percentage >= 90:
        return "Elite"
    elif percentage >= 75:
        return "Excellent"
    elif percentage >= 50:
        return "Good"
    elif percentage >= 25:
        return "Weak"
    else:
        return "Poor"

def get_habit_detail_metrics(created_date, total_logs, selected_date):
    habit_age = (selected_date - created_date).days
    habit_lifetime_days = habit_age + 1
    habit_lifetime_weeks = habit_lifetime_days / 7
    average_logs_per_week = total_logs / habit_lifetime_weeks
    consistency_percentage = total_logs / habit_lifetime_days * 100
    consistency_rating = get_consistency_rating(consistency_percentage)

    return {
        "habit_age": habit_age,
        "average_logs_per_week": average_logs_per_week,
        "consistency_percentage": consistency_percentage,
        "consistency_rating": consistency_rating,
    }

def get_days_since_last_log(last_logged_date, selected_date):
    return (selected_date - last_logged_date).days

def get_habit_status_text(is_archived):
    if is_archived:
        return "Archived"

    return "Active"

def format_streak_display(streak_info):
    current_streak = streak_info["current_streak"]
    longest_streak = streak_info["longest_streak"]

    current_day_word = pluralize(current_streak, "day")
    best_day_word = pluralize(longest_streak, "day")

    return {
        "current_streak": f"{current_streak} {current_day_word}",
        "longest_streak": f"{longest_streak} {best_day_word}",
    }

def format_habit_age(habit_age):
    day_word = pluralize(habit_age, "day")
    return f"{habit_age} {day_word}"

def format_days_since_last_log(days_since_last_log):
    day_word = pluralize(days_since_last_log, "day")
    return f"{days_since_last_log} {day_word}"

def format_consistency_display(percentage, rating):
    return f"{percentage:.2f}% - {rating}"

def format_average_logs_per_week(average_logs_per_week):
    return f"{average_logs_per_week:.2f}"

def get_habit_notes(habits):
    notes = {}

    for habit in habits:
        note = input(f"Enter note for '{habit}' (optional): ").strip()
        notes[habit] = note

    return notes

def get_most_neglected_habit(data, selected_date):
    from validators import validate_date

    most_neglected = None
    highest_days_since = -1

    for habit in data["habits"]:
        details = get_habit_details(data, habit)

        if details["is_archived"]:
            continue

        if details["last_logged_at"] is None:
            continue

        last_logged_date = validate_date(details["last_logged_at"])
        days_since = get_days_since_last_log(last_logged_date, selected_date,)

        if days_since > highest_days_since:
            highest_days_since = days_since
            most_neglected = habit

    if most_neglected is None:
        return None

    return most_neglected, highest_days_since

def format_most_neglected_habit_message(result):
    if result is None:
        return "Most neglected: None yet"

    habit, days_since = result

    return (
        f"- Most neglected: {habit} "
        f"({format_days_since_last_log(days_since)} since last log)")

def get_best_performing_habit(weekly_stats):
    if not weekly_stats:
        return None

    habit_names = sorted(weekly_stats)

    best_habit = habit_names[0]
    best_percentage = weekly_stats[best_habit]["percentage"]

    for habit in habit_names[1:]:
        percentage = weekly_stats[habit]["percentage"]

        if percentage > best_percentage:
            best_habit = habit
            best_percentage = percentage

    return best_habit, best_percentage

def format_best_performing_habit_message(result):
    if result is None:
        return "Best this week: None yet"

    best_habit, best_percentage = result

    return (
        f"- Best this week: {best_habit} "
        f"({best_percentage:.2f}%)")

def get_needs_attention_habit(focus_habits):
    if not focus_habits:
        return None

    return focus_habits[0][0]

def format_needs_attention_habit_message(habit):
    if habit is None:
        return "Needs attention: None"

    return f"⚠️  Needs attention: {habit}"

def get_logs_for_date(data, selected_date):
    selected_date = selected_date.isoformat()

    logs = []

    for log in data["logs"]:
        if log["date"] == selected_date:
            logs.append({
                "habit": log["habit"],
                "note": log.get("note", "")
            })

    return sorted(logs, key=lambda log: log["habit"].lower())

def get_next_habit_id(data):
    habits = data["habits"]

    if not habits:
        return 1

    ids = []

    for habit in habits.values():
        ids.append(habit["id"])

    return max(ids) + 1