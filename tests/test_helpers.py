import pytest
from datetime import date
from validators import validate_date
from config import DEFAULT_SCHEDULED_DAYS
from helpers import (
    get_confirmation,
    is_habit_active_on_date,
    format_display_date,
    show_habits_status,
    pluralize,
    format_weekly_message,
    format_weekly_status,
    get_previous_day_missed_habits,
    habit_has_logs,
    get_habit_details,
    get_today_focus_habits,
    is_habit_at_risk,
    display_weekly_progress_section,
    get_most_neglected_habit,
    get_logs_for_date,
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


def test_show_habits_status_displays_counts(sample_data, monkeypatch):
    sample_data["habits"] = {
        "Workout": {"scheduled_days": DEFAULT_SCHEDULED_DAYS.copy()},
        "Reading": {"scheduled_days": DEFAULT_SCHEDULED_DAYS.copy()},
        "Python": {"scheduled_days": DEFAULT_SCHEDULED_DAYS.copy()}}

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

    show_habits_status(sample_data, result)

    assert "\n✅ Completed habits           Schedule" in messages
    assert "1. Workout                    Everyday" in messages
    assert "2. Reading                    Everyday" in messages
    assert "\n🚫 Unfinished habit           Schedule" in messages
    assert "1. Python                     Everyday" in messages


def test_show_habits_status_displays_only_pending_when_no_completed(sample_data, monkeypatch):
    sample_data["habits"] = {
        "Python": {"scheduled_days": DEFAULT_SCHEDULED_DAYS.copy()}}

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

    show_habits_status(sample_data, result)

    assert "\n✅ Completed" not in messages
    assert "\n🚫 Unfinished habit           Schedule" in messages
    assert "1. Python                     Everyday" in messages


def test_show_habits_status_displays_only_completed_when_no_pending(sample_data, monkeypatch):
    sample_data["habits"] = {
        "Workout": {"scheduled_days": DEFAULT_SCHEDULED_DAYS.copy()}}

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

    show_habits_status(sample_data, result)

    assert "\n✅ Completed habit            Schedule" in messages
    assert "1. Workout                    Everyday" in messages
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
                "scheduled_days": DEFAULT_SCHEDULED_DAYS.copy(),
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
        "scheduled_days": DEFAULT_SCHEDULED_DAYS.copy(),
    }


def test_get_habit_details_for_archived_habit():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": "2026-05-10",
                "scheduled_days": DEFAULT_SCHEDULED_DAYS.copy(),
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
                "scheduled_days": DEFAULT_SCHEDULED_DAYS.copy(),
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


def test_get_habit_details_includes_last_logged_date():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
                "scheduled_days": DEFAULT_SCHEDULED_DAYS.copy(),
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
                "scheduled_days": DEFAULT_SCHEDULED_DAYS.copy(),
            },
        },
        "logs": [],
    }

    result = get_habit_details(data, "Workout")

    assert result["last_logged_at"] is None


def test_get_most_neglected_habit():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 3,
                "created_at": "2026-05-01",
                "archived_at": None,
                "scheduled_days": DEFAULT_SCHEDULED_DAYS.copy(),
            },
            "Reading": {
                "target_per_week": 3,
                "created_at": "2026-05-01",
                "archived_at": None,
                "scheduled_days": DEFAULT_SCHEDULED_DAYS.copy(),
            },
        },
        "logs": [
            {"habit": "Workout", "date": "2026-05-08", "note": ""},
            {"habit": "Reading", "date": "2026-05-01", "note": ""},
        ],
    }

    selected_date = validate_date("2026-05-10")
    result = get_most_neglected_habit(data, selected_date)

    assert result == ("Reading", 9)


def test_get_logs_for_date_includes_notes(sample_data):
    sample_data["logs"] = [
        {
            "habit": "Workout",
            "date": "2026-05-10",
            "note": ""
        },
        {
            "habit": "Reading",
            "date": "2026-05-10",
            "note": "Read chapter 4"
        },
        {
            "habit": "Coding",
            "date": "2026-05-11",
            "note": "Finished exercise"
        }
    ]

    result = get_logs_for_date(
        sample_data,
        date(2026, 5, 10)
    )

    assert result == [
        {
            "habit": "Reading",
            "note": "Read chapter 4"
        },
        {
            "habit": "Workout",
            "note": ""
        }
    ]