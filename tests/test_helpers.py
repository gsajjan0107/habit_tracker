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

    assert result == "✅ completed"


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