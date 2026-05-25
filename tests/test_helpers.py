from datetime import date
import pytest
from helpers import (
    get_confirmation,
    is_habit_active_on_date,
    count_logs_for_habit,
    get_logged_habits_for_date,
    format_display_date,
    pluralize,
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