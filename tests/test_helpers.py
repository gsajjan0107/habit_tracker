from datetime import date
import pytest
from helpers import (
    get_confirmation,
    is_habit_active_on_date,
    count_logs_for_habit,
    get_logged_habits_for_date,
    format_display_date,
    show_habits_status,
    pluralize,
    format_weekly_message,
    format_weekly_status,
    format_daily_summary,
    format_previous_day_missed_message,
    get_sorted_active_habits_from_stats,
    get_previous_day_missed_habits,
    format_log_confirmation_message,
    format_logged_success_message,
    format_streak_line,
    habit_has_logs,
    get_habit_details,
    get_today_focus_habits,
    is_habit_at_risk,
    format_today_focus_message,
    format_weekly_progress_lines,
    get_dashboard_data,
    display_today_focus_section,
    TODAYS_FOCUS_ON_TRACK_MESSAGE,
    display_weekly_progress_section,
    format_no_active_habits_message,
    format_recovery_hint,
    display_completed_today_section,
    display_pending_today_section,
    get_consistency_rating,
    get_habit_detail_metrics,
    get_days_since_last_log,
    get_habit_status_text,
    format_streak_display,
    format_habit_age,
    format_days_since_last_log,
    format_consistency_display,
    format_average_logs_per_week,
)

def test_get_confirmation_yes(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "y")

    assert get_confirmation("Confirm? ") is True


def test_get_confirmation_no(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "n")

    assert get_confirmation("Confirm? ") is False


def test_get_confirmation_invalid_then_yes(monkeypatch):
    answers = iter(["maybe", "yes"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    assert get_confirmation("Confirm? ") is True


def test_is_habit_active_on_date_before_created_date():
    info = {
        "created_at": "2026-05-10",
        "archived_at": None
    }

    assert is_habit_active_on_date(info, "2026-05-09") is False


def test_is_habit_active_on_date_on_created_date():
    info = {
        "created_at": "2026-05-10",
        "archived_at": None
    }

    assert is_habit_active_on_date(info, "2026-05-10") is True


def test_is_habit_active_on_date_between_created_and_archived_date():
    info = {
        "created_at": "2026-05-10",
        "archived_at": "2026-05-15"
    }

    assert is_habit_active_on_date(info, "2026-05-12") is True


def test_is_habit_active_on_date_on_archived_date():
    info = {
        "created_at": "2026-05-10",
        "archived_at": "2026-05-15"
    }

    assert is_habit_active_on_date(info, "2026-05-15") is True


def test_is_habit_active_on_date_after_archived_date():
    info = {
        "created_at": "2026-05-10",
        "archived_at": "2026-05-15"
    }

    assert is_habit_active_on_date(info, "2026-05-16") is False


def test_get_confirmation_yes_returns_true(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "yes")

    assert get_confirmation("Confirm? ") is True


def test_get_confirmation_y_returns_true(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "y")

    assert get_confirmation("Confirm? ") is True


def test_get_confirmation_no_returns_false(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "no")

    assert get_confirmation("Confirm? ") is False


def test_get_confirmation_n_returns_false(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "n")

    assert get_confirmation("Confirm? ") is False


def test_get_confirmation_retries_until_valid(monkeypatch):
    responses = iter(["maybe", "yes"])

    monkeypatch.setattr("builtins.input", lambda _: next(responses))

    assert get_confirmation("Confirm? ") is True


def test_count_logs_for_habit_returns_zero_when_no_logs(sample_data):
    sample_data["habits"] = {
        "Workout": {
            "target_per_week": 3,
            "created_at": "2026-05-01",
            "archived_at": None,
        }
    }
    sample_data["logs"] = []

    assert count_logs_for_habit(sample_data, "Workout") == 0


def test_count_logs_for_habit_counts_only_matching_habit(sample_data):
    sample_data["habits"] = {
        "Workout": {
            "target_per_week": 3,
            "created_at": "2026-05-01",
            "archived_at": None,
        },
        "Reading": {
            "target_per_week": 3,
            "created_at": "2026-05-01",
            "archived_at": None,
        },
    }

    sample_data["logs"] = [
        {"habit": "Workout", "date": "2026-05-01"},
        {"habit": "Workout", "date": "2026-05-02"},
        {"habit": "Reading", "date": "2026-05-01"},
    ]

    assert count_logs_for_habit(sample_data, "Workout") == 2


def test_get_logged_habits_for_date_returns_logged_habits(sample_data):
    sample_data["logs"] = [
        {"habit": "Workout", "date": "2026-05-25"},
        {"habit": "Reading", "date": "2026-05-25"},
        {"habit": "Python", "date": "2026-05-24"},
    ]

    result = get_logged_habits_for_date(sample_data, date(2026, 5, 25))

    assert result == ["Reading", "Workout"]


def test_get_logged_habits_for_date_returns_empty_list_when_no_logs_for_date(sample_data):
    sample_data["logs"] = [
        {"habit": "Workout", "date": "2026-05-24"},
    ]

    result = get_logged_habits_for_date(sample_data, date(2026, 5, 25))

    assert result == []


def test_format_display_date_accepts_string_date():
    result = format_display_date("2026-05-25")

    assert result == "Monday, 25 May 2026"


def test_format_display_date_accepts_date_object():
    result = format_display_date(date(2026, 5, 25))

    assert result == "Monday, 25 May 2026"


def test_format_display_date_rejects_invalid_type():
    with pytest.raises(ValueError, match="Date must be a string or date object."):
        format_display_date(123)


def test_pluralize_returns_singular_for_one():
    assert pluralize(1, "habit") == "habit"


def test_pluralize_returns_plural_for_zero():
    assert pluralize(0, "habit") == "habits"


def test_pluralize_returns_plural_for_more_than_one():
    assert pluralize(2, "habit") == "habits"


def test_pluralize_uses_custom_plural():
    assert pluralize(2, "entry", "entries") == "entries"


def test_show_habits_status_displays_counts(monkeypatch):
    messages = []

    monkeypatch.setattr("helpers.display_message", lambda message: messages.append(message))
    monkeypatch.setattr(
        "helpers.display_numbered_list",
        lambda items: messages.extend([f"{i}. {item}" for i, item in enumerate(items, start=1)])
    )

    result = {
        "completed": ["Workout", "Reading"],
        "pending": ["Python"],
    }

    show_habits_status(result)

    assert "\n✅ Completed (2 habits):" in messages
    assert "1. Reading" in messages
    assert "2. Workout" in messages
    assert "\n🚫 Unfinished (1 habit):" in messages
    assert "1. Python" in messages


def test_show_habits_status_displays_only_pending_when_no_completed(monkeypatch):
    messages = []

    monkeypatch.setattr("helpers.display_message", lambda message: messages.append(message))
    monkeypatch.setattr(
        "helpers.display_numbered_list",
        lambda items: messages.extend([f"{i}. {item}" for i, item in enumerate(items, start=1)])
    )

    result = {
        "completed": [],
        "pending": ["Python"],
    }

    show_habits_status(result)

    assert "\n✅ Completed" not in messages
    assert "\n🚫 Unfinished (1 habit):" in messages
    assert "1. Python" in messages


def test_show_habits_status_displays_only_completed_when_no_pending(monkeypatch):
    messages = []

    monkeypatch.setattr("helpers.display_message", lambda message: messages.append(message))
    monkeypatch.setattr(
        "helpers.display_numbered_list",
        lambda items: messages.extend([f"{i}. {item}" for i, item in enumerate(items, start=1)])
    )

    result = {
        "completed": ["Workout"],
        "pending": [],
    }

    show_habits_status(result)

    assert "\n✅ Completed (1 habit):" in messages
    assert "1. Workout" in messages
    assert "\n🚫 Unfinished" not in messages


def test_format_weekly_message_completed():
    info = {
        "status": "completed",
        "is_possible": True,
        "remaining": 0,
        "available_days_left": 3,
    }

    result = format_weekly_message(info, "✅ completed")

    assert result == "✅  Target met"


def test_format_weekly_message_in_progress_possible():
    info = {
        "status": "in_progress",
        "is_possible": True,
        "remaining": 2,
        "available_days_left": 3,
    }

    result = format_weekly_message(info, "🔄 in progress")

    assert result == "2 more needed, 3 days available - 🔄 in progress"


def test_format_weekly_message_in_progress_possible_one_day_left():
    info = {
        "status": "in_progress",
        "is_possible": True,
        "remaining": 1,
        "available_days_left": 1,
    }

    result = format_weekly_message(info, "🔄 in progress")

    assert result == "1 more needed, 1 day available - 🔄 in progress"


def test_format_weekly_message_not_possible():
    info = {
        "status": "in_progress",
        "is_possible": False,
        "remaining": 4,
        "available_days_left": 1,
    }

    result = format_weekly_message(info, "🔄 in progress")

    assert result == "⚠️  Not possible this week (4 more needed, 1 day available)"


def test_format_weekly_status_completed():
    assert format_weekly_status("completed") == "✅ completed"


def test_format_weekly_status_in_progress():
    assert format_weekly_status("in_progress") == "🔄 in progress"


def test_format_weekly_status_not_started():
    assert format_weekly_status("not_started") == "⚪ not started"


def test_format_weekly_status_unknown_returns_original():
    assert format_weekly_status("paused") == "paused"


def test_format_daily_summary_single_habit():
    result = {
        "total_completed": 1,
        "total_habits": 1,
        "completion_rate": 100.0,
    }

    summary = format_daily_summary(result, "Tuesday, 26 May 2026")

    assert summary == "1/1 habit completed (100.00%) on Tuesday, 26 May 2026."


def test_format_daily_summary_multiple_habits():
    result = {
        "total_completed": 2,
        "total_habits": 4,
        "completion_rate": 50.0,
    }

    summary = format_daily_summary(result, "Tuesday, 26 May 2026")

    assert summary == "2/4 habits completed (50.00%) on Tuesday, 26 May 2026."


def test_format_previous_day_missed_message_single_habit():
    missed = ["Workout"]

    result = format_previous_day_missed_message(date(2026, 5, 25), missed)

    assert result == "Not logged on Monday, 25 May 2026 (1 habit):"


def test_format_previous_day_missed_message_multiple_habits():
    missed = ["Workout", "Reading"]

    result = format_previous_day_missed_message(date(2026, 5, 25), missed)

    assert result == "Not logged on Monday, 25 May 2026 (2 habits):"


def test_show_habits_status_sorts_completed_and_pending(monkeypatch):
    messages = []

    monkeypatch.setattr("helpers.display_message", lambda message: messages.append(message))
    monkeypatch.setattr(
        "helpers.display_numbered_list",
        lambda items: messages.extend(
            [f"{i}. {item}" for i, item in enumerate(items, start=1)]
        )
    )

    result = {
        "completed": ["Workout", "Python", "Reading"],
        "pending": ["Meditation", "Boxing", "Journaling"],
    }

    show_habits_status(result)

    assert "1. Python" in messages
    assert "2. Reading" in messages
    assert "3. Workout" in messages

    assert "1. Boxing" in messages
    assert "2. Journaling" in messages
    assert "3. Meditation" in messages


def test_get_sorted_active_habits_from_stats_returns_sorted_names():
    result = {
        "completed": ["Workout", "Python"],
        "pending": ["Reading", "Boxing"],
    }

    assert get_sorted_active_habits_from_stats(result) == [
        "Boxing",
        "Python",
        "Reading",
        "Workout",
    ]


def test_get_previous_day_missed_habits_returns_sorted_pending():
    def fake_daily_stats(data, selected_date):
        return {
            "total_habits": 3,
            "pending": ["Workout", "Boxing", "Python"],
        }

    previous_day, missed = get_previous_day_missed_habits(
        {},
        date(2026, 5, 26),
        fake_daily_stats
    )

    assert previous_day == date(2026, 5, 25)
    assert missed == ["Boxing", "Python", "Workout"]


def test_get_previous_day_missed_habits_returns_empty_when_no_active_habits():
    def fake_daily_stats(data, selected_date):
        return {
            "total_habits": 0,
            "pending": ["Workout"],
        }

    previous_day, missed = get_previous_day_missed_habits(
        {},
        date(2026, 5, 26),
        fake_daily_stats
    )

    assert previous_day == date(2026, 5, 25)
    assert missed == []


def test_get_previous_day_missed_habits_returns_empty_on_value_error():
    def fake_daily_stats(data, selected_date):
        raise ValueError("No habits created.")

    previous_day, missed = get_previous_day_missed_habits(
        {},
        date(2026, 5, 26),
        fake_daily_stats
    )

    assert previous_day == date(2026, 5, 25)
    assert missed == []


def test_format_log_confirmation_message_single_habit():
    selected_habits = ["Workout"]

    result = format_log_confirmation_message(
        selected_habits,
        "Tuesday, 26 May 2026"
    )

    assert result == "\nYou are about to log 1 habit for Tuesday, 26 May 2026:"


def test_format_log_confirmation_message_multiple_habits():
    selected_habits = ["Workout", "Reading"]

    result = format_log_confirmation_message(
        selected_habits,
        "Tuesday, 26 May 2026"
    )

    assert result == "\nYou are about to log 2 habits for Tuesday, 26 May 2026:"


def test_format_logged_success_message_single_habit():
    logged = ["Workout"]

    result = format_logged_success_message(
        logged,
        "Tuesday, 26 May 2026"
    )

    assert result == "\n✅ Logged 1 habit for Tuesday, 26 May 2026:\n"


def test_format_logged_success_message_multiple_habits():
    logged = ["Workout", "Reading"]

    result = format_logged_success_message(
        logged,
        "Tuesday, 26 May 2026"
    )

    assert result == "\n✅ Logged 2 habits for Tuesday, 26 May 2026:\n"


def test_format_streak_line_single_day():
    result = format_streak_line("Workout", 1)

    assert result == "- Workout: 1 day streak"


def test_format_streak_line_multiple_days():
    result = format_streak_line("Workout", 5)

    assert result == "- Workout: 5 days streak"


def test_habit_has_logs_returns_true_when_habit_has_logs():
    data = {
        "habits": {},
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }

    assert habit_has_logs(data, "Workout") is True


def test_habit_has_logs_returns_false_when_habit_has_no_logs():
    data = {
        "habits": {},
        "logs": [
            {
                "habit": "Reading",
                "date": "2026-05-01",
            }
        ],
    }

    assert habit_has_logs(data, "Workout") is False


def test_get_habit_details_for_active_habit():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            },
            {
                "habit": "Workout",
                "date": "2026-05-02",
            },
        ],
    }

    details = get_habit_details(data, "Workout")

    assert details == {
        "name": "Workout",
        "target_per_week": 5,
        "created_at": "2026-05-01",
        "archived_at": None,
        "is_archived": False,
        "total_logs": 2,
        "last_logged_at": "2026-05-02",
        "description": "",
    }


def test_get_habit_details_for_archived_habit():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": "2026-05-10",
            }
        },
        "logs": [],
    }

    details = get_habit_details(data, "Workout")

    assert details["is_archived"] is True
    assert details["total_logs"] == 0
    assert details["description"] == ""


def test_get_habit_details_returns_stored_description():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
                "description": "Morning strength training",
            },
        },
        "logs": [],
    }

    details = get_habit_details(data, "Workout")

    assert details["description"] == "Morning strength training"


def test_get_habit_details_for_missing_habit_raises_error():
    data = {
        "habits": {},
        "logs": [],
    }

    with pytest.raises(ValueError, match="Habit does not exist"):
        get_habit_details(data, "Workout")


def test_get_today_focus_habits_only_includes_pending_habits_with_remaining_work():
    pending_habits = ["Workout", "Reading", "Coding"]

    weekly_stats = {
        "Workout": {
            "remaining": 0,
            "available_days_left": 3,
        },
        "Reading": {
            "remaining": 2,
            "available_days_left": 3,
        },
        "Coding": {
            "remaining": 1,
            "available_days_left": 3,
        },
    }

    result = get_today_focus_habits(pending_habits, weekly_stats)

    assert result == [
        ("Reading", weekly_stats["Reading"]),
        ("Coding", weekly_stats["Coding"]),
    ]


def test_get_today_focus_habits_sorts_by_urgency():
    pending_habits = ["Reading", "Workout", "Coding"]

    weekly_stats = {
        "Reading": {
            "remaining": 1,
            "available_days_left": 4,
        },
        "Workout": {
            "remaining": 3,
            "available_days_left": 2,
        },
        "Coding": {
            "remaining": 1,
            "available_days_left": 2,
        },
    }

    result = get_today_focus_habits(pending_habits, weekly_stats)

    assert result == [
        ("Workout", weekly_stats["Workout"]),
        ("Coding", weekly_stats["Coding"]),
        ("Reading", weekly_stats["Reading"]),
    ]


def test_get_today_focus_habits_ignores_pending_habits_missing_from_weekly_stats():
    pending_habits = ["Workout", "Reading"]

    weekly_stats = {
        "Workout": {
            "remaining": 1,
            "available_days_left": 3,
        },
    }

    result = get_today_focus_habits(pending_habits, weekly_stats)

    assert result == [
        ("Workout", weekly_stats["Workout"]),
    ]


def test_is_habit_at_risk_returns_true_when_remaining_exceeds_available_days():
    info = {
        "remaining": 4,
        "available_days_left": 3,
    }

    assert is_habit_at_risk(info) is True


def test_is_habit_at_risk_returns_false_when_remaining_can_fit_available_days():
    info = {
        "remaining": 3,
        "available_days_left": 3,
    }

    assert is_habit_at_risk(info) is False


def test_format_today_focus_message_without_risk():
    info = {
        "remaining": 2,
        "available_days_left": 3,
    }

    result = format_today_focus_message("Coding", info)

    assert result == "- Coding: 2 more needed this week, 3 days available"


def test_format_today_focus_message_with_risk():
    info = {
        "remaining": 4,
        "available_days_left": 3,
    }

    result = format_today_focus_message("Coding", info)

    assert result == "- Coding: 4 more needed this week, 3 days available ⚠️  At risk"


def test_format_today_focus_message_uses_singular_day():
    info = {
        "remaining": 1,
        "available_days_left": 1,
    }

    result = format_today_focus_message("Workout", info)

    assert result == "- Workout: 1 more needed this week, 1 day available"


def test_format_weekly_progress_lines_for_completed_target():
    info = {
        "done": 5,
        "target": 5,
        "percentage": 100.0,
        "status": "completed",
        "remaining": 0,
        "available_days_left": 3,
        "is_possible": True,
    }

    streak_info = {
        "current_streak": 4,
        "longest_streak": 10,
    }

    result = format_weekly_progress_lines("Coding", info, streak_info)

    assert result == [
        "\nCoding         ",
        "  Weekly :  5/5  (100.00%) - ✅  Target met",
        "  Streak : 🔥 4",
        "  Best   : 🏆 10",
    ]


def test_format_weekly_progress_lines_for_at_risk_target():
    info = {
        "done": 1,
        "target": 5,
        "percentage": 20.0,
        "status": "behind",
        "remaining": 4,
        "available_days_left": 3,
        "is_possible": False,
    }

    streak_info = {
        "current_streak": 0,
        "longest_streak": 6,
    }

    result = format_weekly_progress_lines("Reading", info, streak_info)

    assert result == [
        "\nReading        ",
        "  Weekly :  1/5  (20.00%) - ⚠️  Not possible this week (4 more needed, 3 days available)",
        "  Streak : 🔥 0",
        "  Best   : 🏆 6",
    ]


def test_get_dashboard_data_returns_daily_weekly_and_streaks():
    data = {
        "schema_version": 1,
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
            "Reading": {
                "target_per_week": 3,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            },
        ],
    }

    result = get_dashboard_data(data, "2026-05-01")

    assert set(result.keys()) == {"daily", "weekly", "streaks"}

    assert result["daily"]["date"] == "2026-05-01"
    assert result["daily"]["completed"] == ["Workout"]
    assert result["daily"]["pending"] == ["Reading"]

    assert "Workout" in result["weekly"]
    assert "Reading" in result["weekly"]

    assert "Workout" in result["streaks"]
    assert "Reading" in result["streaks"]


def test_display_today_focus_section_shows_focus_habits(capsys):
    focus_habits = [
        (
            "Coding",
            {
                "remaining": 2,
                "available_days_left": 3,
            },
        ),
        (
            "Workout",
            {
                "remaining": 4,
                "available_days_left": 3,
            },
        ),
    ]

    display_today_focus_section(focus_habits)

    output = capsys.readouterr().out

    assert "🎯 Today's Focus" in output
    assert "- Coding: 2 more needed this week, 3 days available" in output
    assert "- Workout: 4 more needed this week, 3 days available ⚠️  At risk" in output


def test_display_today_focus_section_shows_on_track_message_when_empty(capsys):
    display_today_focus_section([])

    output = capsys.readouterr().out

    assert "🎯 Today's Focus" in output
    assert TODAYS_FOCUS_ON_TRACK_MESSAGE in output


def test_display_weekly_progress_section_shows_weekly_stats_and_streaks(capsys):
    active_habits = ["Coding"]

    weekly_stats = {
        "Coding": {
            "done": 5,
            "target": 5,
            "percentage": 100.0,
            "status": "completed",
            "remaining": 0,
            "available_days_left": 3,
            "is_possible": True,
        },
    }

    habit_streaks = {
        "Coding": {
            "current_streak": 4,
            "longest_streak": 10,
        },
    }

    display_weekly_progress_section(active_habits, weekly_stats, habit_streaks)

    output = capsys.readouterr().out

    assert "📊 Weekly Progress (1 habit):" in output
    assert "Coding" in output
    assert "Weekly :  5/5" in output
    assert "✅  Target met" in output
    assert "Streak : 🔥 4" in output
    assert "Best   : 🏆 10" in output


def test_display_weekly_progress_section_uses_zero_streaks_when_missing(capsys):
    active_habits = ["Reading"]

    weekly_stats = {
        "Reading": {
            "done": 1,
            "target": 3,
            "percentage": 33.33,
            "status": "in_progress",
            "remaining": 2,
            "available_days_left": 3,
            "is_possible": True,
        },
    }

    habit_streaks = {}

    display_weekly_progress_section(active_habits, weekly_stats, habit_streaks)

    output = capsys.readouterr().out

    assert "📊 Weekly Progress (1 habit):" in output
    assert "Reading" in output
    assert "Weekly :  1/3" in output
    assert "2 more needed, 3 days available" in output
    assert "Streak : 🔥 0" in output
    assert "Best   : 🏆 0" in output


def test_format_no_active_habits_message():
    result = format_no_active_habits_message("Friday, 01 May 2026")

    assert result == "No habits were active on Friday, 01 May 2026."


def test_format_recovery_hint_no_missed_habits():
    assert format_recovery_hint([]) == ""


def test_format_recovery_hint_single_missed_habit():
    assert (
        format_recovery_hint(["Coding"])
        == "Recovery hint: Pick the easiest missed habit and complete it first today."
    )


def test_format_recovery_hint_multiple_missed_habits():
    assert (
        format_recovery_hint(["Coding", "Workout"])
        == "Recovery hint: Pick the easiest missed habits and complete it first today."
    )


def test_display_completed_today_section_shows_completed_habits(capsys):
    display_completed_today_section(["Coding", "Workout"])

    output = capsys.readouterr().out

    assert "✅ Completed Today" in output
    assert "1. Coding" in output
    assert "2. Workout" in output


def test_display_completed_today_section_shows_empty_message(capsys):
    display_completed_today_section([])

    output = capsys.readouterr().out

    assert "✅ Completed Today" in output
    assert "No habits completed yet today." in output


def test_display_pending_today_section_shows_pending_habits(capsys):
    display_pending_today_section(["Reading", "Workout"])

    output = capsys.readouterr().out

    assert "⏳ Pending Today" in output
    assert "1. Reading" in output
    assert "2. Workout" in output


def test_display_pending_today_section_shows_empty_message(capsys):
    display_pending_today_section([])

    output = capsys.readouterr().out

    assert "⏳ Pending Today" in output
    assert "All active habits completed for today." in output


def test_get_habit_details_includes_last_logged_date():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
        },
        "logs": [
            {"habit": "Workout", "date": "2026-05-01"},
            {"habit": "Workout", "date": "2026-05-03"},
            {"habit": "Workout", "date": "2026-05-02"},
        ],
    }

    result = get_habit_details(data, "Workout")

    assert result["last_logged_at"] == "2026-05-03"


def test_get_habit_details_has_no_last_logged_date_when_never_logged():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
        },
        "logs": [],
    }

    result = get_habit_details(data, "Workout")

    assert result["last_logged_at"] is None


def test_get_consistency_rating_returns_correct_labels():
    assert get_consistency_rating(100) == "Elite"
    assert get_consistency_rating(90) == "Elite"
    assert get_consistency_rating(89.99) == "Excellent"
    assert get_consistency_rating(75) == "Excellent"
    assert get_consistency_rating(74.99) == "Good"
    assert get_consistency_rating(50) == "Good"
    assert get_consistency_rating(49.99) == "Weak"
    assert get_consistency_rating(25) == "Weak"
    assert get_consistency_rating(24.99) == "Poor"
    assert get_consistency_rating(0) == "Poor"


def test_get_habit_detail_metrics_returns_age_average_and_consistency():
    created_date = date(2026, 5, 1)
    selected_date = date(2026, 5, 10)

    metrics = get_habit_detail_metrics(
        created_date,
        total_logs=6,
        selected_date=selected_date,
    )

    assert metrics["habit_age"] == 9
    assert metrics["average_logs_per_week"] == 4.2
    assert metrics["consistency_percentage"] == 60.0
    assert metrics["consistency_rating"] == "Good"


def test_get_days_since_last_log_returns_day_difference():
    last_logged_date = date(2026, 5, 8)
    selected_date = date(2026, 5, 10)

    assert get_days_since_last_log(last_logged_date, selected_date) == 2


def test_get_habit_status_text_returns_active_or_archived():
    assert get_habit_status_text(False) == "Active"
    assert get_habit_status_text(True) == "Archived"


def test_format_streak_display_returns_pluralized_streak_text():
    streak_info = {
        "current_streak": 1,
        "longest_streak": 3,
    }

    result = format_streak_display(streak_info)

    assert result["current_streak"] == "1 day"
    assert result["longest_streak"] == "3 days"


def test_format_habit_age_returns_pluralized_age_text():
    assert format_habit_age(1) == "1 day"
    assert format_habit_age(9) == "9 days"
    assert format_habit_age(0) == "0 days"


def test_format_days_since_last_log_returns_pluralized_text():
    assert format_days_since_last_log(0) == "0 days"
    assert format_days_since_last_log(1) == "1 day"
    assert format_days_since_last_log(2) == "2 days"


def test_format_consistency_display_returns_percentage_and_rating():
    assert format_consistency_display(60, "Good") == "60.00% - Good"
    assert format_consistency_display(100, "Elite") == "100.00% - Elite"
    assert format_consistency_display(24.987, "Poor") == "24.99% - Poor"


def test_format_average_logs_per_week_returns_two_decimal_text():
    assert format_average_logs_per_week(2.1) == "2.10"
    assert format_average_logs_per_week(0) == "0.00"
    assert format_average_logs_per_week(7) == "7.00"