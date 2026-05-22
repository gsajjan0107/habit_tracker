import pytest
from habits import (
    add_habit,
    log_habit,
    archive_habit,
    unarchive_habit,
    toggle_archive_habit,
    delete_log,
    delete_habit
    )


def test_add_habit_success(sample_data):

    result = add_habit(sample_data, "Workout", 5)

    assert result == "Workout added."
    assert "Workout" in sample_data["habits"]

    habit = sample_data["habits"]["Workout"]

    assert habit["target_per_week"] == 5
    assert habit["archived_at"] is None


def test_add_duplicate_active_habit(sample_data):
    add_habit(sample_data, "Workout", 5)

    with pytest.raises(ValueError, match="Habit already exists."):
        add_habit(sample_data, "Workout", 3)


def test_add_archived_habit():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-10",
                "archived_at": "2026-05-11"
            }
        }
    }

    with pytest.raises(ValueError, match="Habit exists but is archived."):
        add_habit(data, "Workout", 3)


def test_add_habit_invalid_name(sample_data):

    with pytest.raises(ValueError):
        add_habit(sample_data, "", 5)


def test_add_habit_invalid_target(sample_data):

    with pytest.raises(ValueError):
        add_habit(sample_data, "Workout", 0)


def test_log_habit_success(sample_data):
    add_habit(sample_data, "Reading", 30)

    result = log_habit(sample_data, "2026-05-10", "Reading")

    assert result == "Reading logged for 2026-05-10."

    assert len(sample_data["logs"]) == 1

    assert sample_data["logs"][0] == {
        "habit": "Reading",
        "date": "2026-05-10"
    }


def test_log_habit_duplicate_same_day(sample_data):
    add_habit(sample_data, "Reading", 30)

    log_habit(sample_data, "2026-05-10", "Reading")

    with pytest.raises(ValueError) as exc:
        log_habit(sample_data, "2026-05-10", "Reading")

    assert str(exc.value) == "Habit already logged for this date."


def test_log_habit_nonexistent_habit(sample_data):
    add_habit(sample_data, "Workout", 7)

    with pytest.raises(ValueError) as exc:
        log_habit(sample_data, "2026-05-10", "Reading")

    assert str(exc.value) == "Habit does not exist."


def test_log_habit_archived_habit(sample_data):
    add_habit(sample_data, "Reading", 30)

    sample_data["habits"]["Reading"]["archived_at"] = "2026-05-10"

    with pytest.raises(ValueError) as exc:
        log_habit(sample_data, "2026-05-10", "Reading")

    assert str(exc.value) == "Cannot log as the habit is archived."


def test_log_habit_before_creation_date(sample_data):
    add_habit(sample_data, "Reading", 30)

    sample_data["habits"]["Reading"]["created_at"] = "2026-05-10"

    with pytest.raises(ValueError) as exc:
        log_habit(sample_data, "2026-05-09", "Reading")

    assert str(exc.value) == (
        "Habit cannot be logged before it was created."
    )


def test_log_habit_empty_data(sample_data, capsys):
    result = log_habit(sample_data, "2026-05-10", "Reading")

    captured = capsys.readouterr()

    assert result is None

    assert (
        "No habits found. Add a habit first."
        in captured.out
    )


def test_archive_habit_success(sample_data):
    add_habit(sample_data, "Workout", 5)

    result = archive_habit(sample_data, "Workout")

    assert result["success"] is True
    assert result["msg"] == "Workout archived."
    assert result["data"]["habit"] == "Workout"
    assert result["data"]["archived"] is True


def test_archive_nonexistent_habit(sample_data):
    result = archive_habit(sample_data, "Workout")

    assert result["success"] is False
    assert result["msg"] == "Habit does not exist."
    assert result["data"]["habit"] == "Workout"


def test_archive_already_archived_habit(sample_data):
    add_habit(sample_data, "Workout", 5)
    archive_habit(sample_data, "Workout")

    result = archive_habit(sample_data, "Workout")

    assert result["success"] is False
    assert result["msg"] == "Habit already archived."
    assert result["data"]["archived"] is True


def test_unarchive_habit_success(sample_data):
    add_habit(sample_data, "Workout", 5)

    result = unarchive_habit(sample_data, "Workout")

    assert result["success"] is False
    assert result["msg"] == "Habit already active."
    assert result["data"]["archived"] is False


def test_unarchive_nonexistent_habit(sample_data):
    result = archive_habit(sample_data, "Workout")

    assert result["success"] is False
    assert result["msg"] == "Habit does not exist."
    assert result["data"]["habit"] == "Workout"


def test_unarchive_already_active_habit(sample_data):
    add_habit(sample_data, "Workout", 5)
    result = unarchive_habit(sample_data, "Workout")

    assert result["success"] is False
    assert result["msg"] == "Habit already active."
    assert result["data"]["archived"] is False


def test_archive_does_not_delete_habit(sample_data):
    add_habit(sample_data, "Workout", 5)

    archive_habit(sample_data, "Workout")

    assert "Workout" in sample_data["habits"]


def test_delete_log_success(sample_data):
    add_habit(sample_data, "Workout", 5)

    log_habit(sample_data, "2026-05-10", "Workout")

    result = delete_log(sample_data, "2026-05-10", "Workout")

    assert result == "Log of Workout for 2026-05-10 deleted."
    assert sample_data["logs"] == []


def test_delete_log_no_habits(sample_data):
    result = delete_log(sample_data, "2026-05-10", "Workout")

    assert result == "No habits found. Add a habit first."


def test_delete_log_no_logs(sample_data):
    add_habit(sample_data, "Workout", 5)

    result = delete_log(sample_data, "2026-05-10", "Workout")

    assert result == "No logs found. Log a habit first."


def test_delete_log_no_matching_log(sample_data):
    add_habit(sample_data, "Workout", 5)
    sample_data["habits"]["Workout"]["created_at"] = "2026-05-09"

    log_habit(sample_data, "2026-05-09", "Workout")

    result = delete_log(sample_data, "2026-05-10", "Workout")

    assert result == "No matching log found."

    assert len(sample_data["logs"]) == 1


def test_delete_log_only_removes_matching_log(sample_data):
    add_habit(sample_data, "Workout", 5)
    add_habit(sample_data, "Reading", 3)

    log_habit(sample_data, "2026-05-10", "Workout")
    log_habit(sample_data, "2026-05-10", "Reading")

    result = delete_log(sample_data, "2026-05-10", "Workout")

    assert result == "Log of Workout for 2026-05-10 deleted."

    assert len(sample_data["logs"]) == 1

    remaining_log = sample_data["logs"][0]

    assert remaining_log["habit"] == "Reading"


def test_delete_log_invalid_date(sample_data):
    add_habit(sample_data, "Workout", 5)

    log_habit(sample_data, "2026-05-10", "Workout")

    with pytest.raises(ValueError):
        delete_log(sample_data, "invalid-date", "Workout")


def test_delete_habit_success(sample_data):
    add_habit(sample_data, "Reading", 30)

    result = delete_habit(sample_data, "Reading")

    assert result == "Reading deleted."

    assert "Reading" not in sample_data["habits"]


def test_delete_habit_removes_related_logs(sample_data):
    add_habit(sample_data, "Reading", 30)
    add_habit(sample_data, "Workout", 30)

    sample_data["logs"] = [
        {
            "habit": "Reading",
            "date": "2026-05-10"
        },
        {
            "habit": "Workout",
            "date": "2026-05-10"
        }
    ]

    delete_habit(sample_data, "Reading")

    assert len(sample_data["logs"]) == 1

    assert sample_data["logs"][0] == {
        "habit": "Workout",
        "date": "2026-05-10"
    }


def test_delete_nonexistent_habit(sample_data):
    with pytest.raises(ValueError) as exc:
        delete_habit(sample_data, "Reading")

    assert str(exc.value) == "Habit does not exist."


def test_delete_habit_with_multiple_logs(sample_data):
    add_habit(sample_data, "Reading", 30)

    sample_data["logs"] = [
        {
            "habit": "Reading",
            "date": "2026-05-08"
        },
        {
            "habit": "Reading",
            "date": "2026-05-09"
        },
        {
            "habit": "Reading",
            "date": "2026-05-10"
        }
    ]

    delete_habit(sample_data, "Reading")

    assert sample_data["logs"] == []

    assert "Reading" not in sample_data["habits"]


def test_toggle_archive_nonexistent_habit(sample_data):
    result = toggle_archive_habit(sample_data, "Workout")

    assert result["success"] is False
    assert result["msg"] == "Habit does not exist."
    assert result["data"]["habit"] == "Workout"