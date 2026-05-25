from helpers import get_confirmation, is_habit_active_on_date


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