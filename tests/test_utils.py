from utils import build_archive_menu_entries, get_selected_habits, handle_operation_result, format_habit_label

def test_build_archive_menu_entries_puts_active_habits_before_archived(sample_data):
    sample_data["habits"] = {
        "A Archived": {
            "target_per_week": 3,
            "created_at": "2026-05-01",
            "archived_at": "2026-05-10",
        },
        "B Active": {
            "target_per_week": 3,
            "created_at": "2026-05-01",
            "archived_at": None,
        },
    }

    habits = sorted(sample_data["habits"])

    result = build_archive_menu_entries(sample_data, habits)

    assert result == [
        {"habit": "B Active", "archived": False},
        {"habit": "A Archived", "archived": True},
    ]


def test_get_selected_habits_selects_single_habit(monkeypatch):
    pending = ["Workout", "Reading", "Coding"]

    monkeypatch.setattr("builtins.input", lambda _: "2")

    result = get_selected_habits(pending)

    assert result == ["Reading"]


def test_get_selected_habits_selects_multiple_habits(monkeypatch):
    pending = ["Workout", "Reading", "Coding"]

    monkeypatch.setattr("builtins.input", lambda _: "1 3")

    result = get_selected_habits(pending)

    assert result == ["Workout", "Coding"]


def test_get_selected_habits_selects_all(monkeypatch):
    pending = ["Workout", "Reading", "Coding"]

    monkeypatch.setattr("builtins.input", lambda _: "all")

    result = get_selected_habits(pending)

    assert result == pending


def test_get_selected_habits_returns_none_when_cancelled(monkeypatch):
    pending = ["Workout", "Reading", "Coding"]

    monkeypatch.setattr("builtins.input", lambda _: "q")

    result = get_selected_habits(pending)

    assert result is None


def test_get_selected_habits_ignores_duplicate_numbers(monkeypatch):
    pending = ["Workout", "Reading", "Coding"]

    monkeypatch.setattr("builtins.input", lambda _: "1 1 2")

    result = get_selected_habits(pending)

    assert result == ["Workout", "Reading"]


def test_get_selected_habits_retries_after_invalid_input(monkeypatch):
    pending = ["Workout", "Reading", "Coding"]

    inputs = iter(["9", "2"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    result = get_selected_habits(pending)

    assert result == ["Reading"]


def test_get_selected_habits_retries_after_blank_input(monkeypatch):
    pending = ["Workout", "Reading", "Coding"]

    inputs = iter(["", "2"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    result = get_selected_habits(pending)

    assert result == ["Reading"]


def test_handle_operation_result_saves_data_when_successful(monkeypatch, sample_data):
    saved = {"called": False}

    def fake_save_data(data):
        saved["called"] = True
        assert data == sample_data

    monkeypatch.setattr("utils.save_data", fake_save_data)

    result = {
        "success": True,
        "msg": "Habit archived.",
    }

    handle_operation_result(sample_data, result)

    assert saved["called"] is True


def test_handle_operation_result_does_not_save_data_when_unsuccessful(monkeypatch, sample_data):
    saved = {"called": False}

    def fake_save_data(data):
        saved["called"] = True

    monkeypatch.setattr("utils.save_data", fake_save_data)

    result = {
        "success": False,
        "msg": "Habit not found.",
    }

    handle_operation_result(sample_data, result)

    assert saved["called"] is False


def test_format_habit_label_shows_unarchived_habit():
    result = format_habit_label("Workout", False)

    assert result == "Workout (unarchived)"


def test_format_habit_label_shows_archived_habit():
    result = format_habit_label("Workout", True)

    assert result == "Workout (archived)"