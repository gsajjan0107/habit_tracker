import pytest
from habits import (
    add_habit,
    log_habit,
    log_multiple_habits,
    archive_habit,
    unarchive_habit,
    toggle_archive_habit,
    delete_log,
    delete_habit,
    rename_habit,
    update_habit_target,
    get_habit_logs,
    update_habit_description,
    )


# add_habit tests

def test_add_habit_success(sample_data):
    result = add_habit(sample_data, "Workout", 5)

    assert result == "Workout added."
    assert "Workout" in sample_data["habits"]

    habit = sample_data["habits"]["Workout"]

    assert habit["target_per_week"] == 5
    assert habit["created_at"] == "2026-05-10"
    assert habit["archived_at"] is None


def test_add_habit_strips_habit_name(sample_data):
    result = add_habit(sample_data, "  Workout  ", 5)

    assert result == "Workout added."
    assert "Workout" in sample_data["habits"]
    assert "  Workout  " not in sample_data["habits"]


def test_add_habit_converts_string_target_to_int(sample_data):
    add_habit(sample_data, "Workout", "5")

    habit = sample_data["habits"]["Workout"]

    assert habit["target_per_week"] == 5


def test_add_habit_accepts_minimum_target(sample_data):
    result = add_habit(sample_data, "Workout", 1)

    assert result == "Workout added."
    assert sample_data["habits"]["Workout"]["target_per_week"] == 1


def test_add_habit_accepts_minimum_length_name(sample_data):
    result = add_habit(sample_data, "Run", 3)

    assert result == "Run added."
    assert "Run" in sample_data["habits"]


def test_add_habit_accepts_maximum_length_name(sample_data):
    habit_name = "A" * 20

    result = add_habit(sample_data, habit_name, 3)

    assert result == f"{habit_name.title()} added."
    assert habit_name.title() in sample_data["habits"]


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
                "archived_at": "2026-05-11",
                "description": ""
            }
        }
    }

    with pytest.raises(ValueError, match="Habit exists but is archived. Unarchive it instead."):
        add_habit(data, "Workout", 3)


def test_add_habit_invalid_name(sample_data):

    with pytest.raises(ValueError, match="Cannot be empty."):
        add_habit(sample_data, "", 5)


def test_add_habit_invalid_target(sample_data):

    with pytest.raises(ValueError, match="Input number must be >= 1"):
        add_habit(sample_data, "Workout", 0)


def test_add_habit_stores_description(sample_data):
    add_habit(
        sample_data,
        "Workout",
        5,
        "Strength training"
    )

    assert (
        sample_data["habits"]["Workout"]["description"]
        == "Strength training"
    )


def test_add_habit_uses_empty_description_by_default(sample_data):
    add_habit(sample_data, "Workout", 5)

    assert (
        sample_data["habits"]["Workout"]["description"]
        == ""
    )


# log_habit tests

def test_log_habit_success(sample_data):
    add_habit(sample_data, "Reading", 30)

    result = log_habit(sample_data, "2026-05-10", "Reading")

    assert result == "Reading logged for 2026-05-10."

    assert len(sample_data["logs"]) == 1

    assert sample_data["logs"][0] == {
        "habit": "Reading",
        "date": "2026-05-10",
        "note": ""
    }


def test_log_habit_duplicate_same_day(sample_data):
    add_habit(sample_data, "Reading", 30)

    log_habit(sample_data, "2026-05-10", "Reading")

    with pytest.raises(ValueError) as exc:
        log_habit(sample_data, "2026-05-10", "Reading")

    assert str(exc.value) == "Habit already logged for this date."


def test_log_habit_different_dates_allowed(sample_data):
    add_habit(sample_data, "Reading", 30)

    sample_data["habits"]["Reading"]["created_at"] = "2026-05-01"

    log_habit(sample_data, "2026-05-09", "Reading")
    log_habit(sample_data, "2026-05-10", "Reading")

    assert len(sample_data["logs"]) == 2


def test_log_multiple_habits_same_date(sample_data):
    add_habit(sample_data, "Reading", 30)
    add_habit(sample_data, "Workout", 7)

    log_habit(sample_data, "2026-05-10", "Reading")
    log_habit(sample_data, "2026-05-10", "Workout")

    assert len(sample_data["logs"]) == 2


def test_log_habit_nonexistent_habit(sample_data):
    add_habit(sample_data, "Workout", 7)

    with pytest.raises(ValueError) as exc:
        log_habit(sample_data, "2026-05-10", "Reading")

    assert str(exc.value) == "Habit does not exist."


def test_log_habit_after_archive_date_fails(sample_data):
    add_habit(sample_data, "Reading", 30)

    sample_data["habits"]["Reading"]["created_at"] = "2020-05-01"
    sample_data["habits"]["Reading"]["archived_at"] = "2020-05-10"

    with pytest.raises(ValueError) as exc:
        log_habit(sample_data, "2020-05-11", "Reading")

    assert str(exc.value) == "Cannot log after the habit was archived."


def test_log_habit_before_archive_date_success(sample_data):
    add_habit(sample_data, "Reading", 30)

    sample_data["habits"]["Reading"]["created_at"] = "2020-05-01"
    sample_data["habits"]["Reading"]["archived_at"] = "2020-05-10"

    result = log_habit(sample_data, "2020-05-08", "Reading")

    assert result == "Reading logged for 2020-05-08."
    assert sample_data["logs"] == [
        {
            "habit": "Reading",
            "date": "2020-05-08",
            "note": ""
        }
    ]


def test_log_habit_on_archive_date_success(sample_data):
    add_habit(sample_data, "Reading", 30)

    sample_data["habits"]["Reading"]["created_at"] = "2020-05-01"
    sample_data["habits"]["Reading"]["archived_at"] = "2020-05-10"

    result = log_habit(sample_data, "2020-05-10", "Reading")

    assert result == "Reading logged for 2020-05-10."


def test_log_habit_before_creation_date(sample_data):
    add_habit(sample_data, "Reading", 30)

    sample_data["habits"]["Reading"]["created_at"] = "2026-05-10"

    with pytest.raises(ValueError) as exc:
        log_habit(sample_data, "2026-05-09", "Reading")

    assert str(exc.value) == (
        "Habit cannot be logged before it was created."
    )


def test_log_habit_no_habits_fails(sample_data):
    with pytest.raises(ValueError) as exc:
        log_habit(sample_data, "2020-05-10", "Workout")

    assert str(exc.value) == "No habits found. Add a habit first."


def test_log_habit_on_creation_date(sample_data):
    add_habit(sample_data, "Reading", 30)

    result = log_habit(sample_data, "2026-05-10", "Reading")

    assert result == "Reading logged for 2026-05-10."


def test_log_habit_invalid_date(sample_data):
    add_habit(sample_data, "Reading", 30)

    with pytest.raises(ValueError):
        log_habit(sample_data, "banana", "Reading")


# log_multiple_habits tests

def test_log_multiple_habits_rolls_back_if_one_fails(sample_data):
    add_habit(sample_data, "Workout", 5)

    with pytest.raises(ValueError):
        log_multiple_habits(sample_data, "2020-05-10", ["Workout", "Reading"], {"Workout": ""})

    assert sample_data["logs"] == []


def test_log_multiple_habits_success(sample_data):
    add_habit(sample_data, "Workout", 5)
    add_habit(sample_data, "Reading", 7)

    result = log_multiple_habits(
        sample_data,
        "2026-05-10",
        ["Workout", "Reading"],
        {
            "Workout": "",
            "Reading": "",
        }
    )

    assert result == ["Workout", "Reading"]

    assert sample_data["logs"] == [
        {
            "habit": "Workout",
            "date": "2026-05-10",
            "note": ""
        },
        {
            "habit": "Reading",
            "date": "2026-05-10",
            "note": ""
        }
    ]


def test_log_multiple_habits_restores_existing_logs_on_failure(sample_data):
    add_habit(sample_data, "Workout", 5)

    sample_data["logs"] = [
        {
            "habit": "Workout",
            "date": "2020-05-01"
        }
    ]

    with pytest.raises(ValueError):
        log_multiple_habits(
            sample_data,
            "2020-05-10",
            ["Workout", "Reading"],
            {
                "Workout": "",
                "Reading": ""
            }
        )

    assert sample_data["logs"] == [
        {
            "habit": "Workout",
            "date": "2020-05-01"
        }
    ]


# archive_habit tests

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


def test_archive_does_not_delete_habit(sample_data):
    add_habit(sample_data, "Workout", 5)

    archive_habit(sample_data, "Workout")

    assert "Workout" in sample_data["habits"]


def test_archive_habit_before_creation_date_fails(sample_data):
    add_habit(sample_data, "Workout", 5)
    sample_data["habits"]["Workout"]["created_at"] = "2026-05-10"

    result = archive_habit(sample_data, "Workout", "2026-05-09")

    assert result["success"] is False
    assert result["msg"] == "Habit cannot be archived before it was created."
    assert result["data"]["habit"] == "Workout"
    assert sample_data["habits"]["Workout"]["archived_at"] is None


# unarchive_habit tests

def test_unarchive_habit_success(sample_data):
    add_habit(sample_data, "Workout", 5)
    archive_habit(sample_data, "Workout")

    result = unarchive_habit(sample_data, "Workout")

    assert result["success"] is True
    assert result["msg"] == "Workout unarchived."
    assert result["data"]["habit"] == "Workout"
    assert result["data"]["archived"] is False
    assert sample_data["habits"]["Workout"]["archived_at"] is None


def test_unarchive_nonexistent_habit(sample_data):
    result = unarchive_habit(sample_data, "Workout")

    assert result["success"] is False
    assert result["msg"] == "Habit does not exist."
    assert result["data"]["habit"] == "Workout"


def test_unarchive_already_active_habit(sample_data):
    add_habit(sample_data, "Workout", 5)
    result = unarchive_habit(sample_data, "Workout")

    assert result["success"] is False
    assert result["msg"] == "Habit already active."
    assert result["data"]["archived"] is False


# toggle_archive_habit tests

def test_toggle_archive_nonexistent_habit(sample_data):
    result = toggle_archive_habit(sample_data, "Workout")

    assert result["success"] is False
    assert result["msg"] == "Habit does not exist."
    assert result["data"]["habit"] == "Workout"


def test_toggle_archive_active_habit_archives_it(sample_data):
    add_habit(sample_data, "Workout", 5)

    result = toggle_archive_habit(sample_data, "Workout")

    assert result["success"] is True
    assert result["msg"] == "Workout archived."
    assert result["data"]["habit"] == "Workout"
    assert result["data"]["archived"] is True
    assert sample_data["habits"]["Workout"]["archived_at"] is not None


def test_toggle_archive_archived_habit_unarchives_it(sample_data):
    add_habit(sample_data, "Workout", 5)
    archive_habit(sample_data, "Workout")

    result = toggle_archive_habit(sample_data, "Workout")

    assert result["success"] is True
    assert result["msg"] == "Workout unarchived."
    assert result["data"]["habit"] == "Workout"
    assert result["data"]["archived"] is False
    assert sample_data["habits"]["Workout"]["archived_at"] is None


# delete_log tests

def test_delete_log_success(sample_data):
    add_habit(sample_data, "Workout", 5)

    log_habit(sample_data, "2026-05-10", "Workout")

    result = delete_log(sample_data, "2026-05-10", "Workout")

    assert result == "Log of Workout for 2026-05-10 deleted."
    assert sample_data["logs"] == []


def test_delete_log_no_logs(sample_data):
    add_habit(sample_data, "Workout", 5)

    with pytest.raises(ValueError) as exc:
        delete_log(sample_data, "2020-05-10", "Workout")

    assert str(exc.value) == "No logs found. Log a habit first."


def test_delete_log_no_matching_log(sample_data):
    add_habit(sample_data, "Workout", 5)

    sample_data["habits"]["Workout"]["created_at"] = "2020-05-01"

    log_habit(sample_data, "2020-05-09", "Workout")

    with pytest.raises(ValueError) as exc:
        delete_log(sample_data, "2020-05-10", "Workout")

    assert str(exc.value) == "No matching log found."


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


def test_delete_log_nonexistent_habit_fails(sample_data):
    add_habit(sample_data, "Workout", 5)

    with pytest.raises(ValueError) as exc:
        delete_log(sample_data, "2020-05-10", "Reading")

    assert str(exc.value) == "Habit does not exist."


def test_delete_log_invalid_habit_name_fails(sample_data):
    add_habit(sample_data, "Workout", 5)

    with pytest.raises(ValueError):
        delete_log(sample_data, "2020-05-10", "A")


def test_delete_log_no_habits_fails(sample_data):
    with pytest.raises(ValueError) as exc:
        delete_log(sample_data, "2020-05-10", "Workout")

    assert str(exc.value) == "No habits found. Add a habit first."


# delete_habit tests

def test_delete_habit_success(sample_data):
    add_habit(sample_data, "Reading", 30)

    result = delete_habit(sample_data, "Reading")

    assert result == "Reading deleted."

    assert "Reading" not in sample_data["habits"]


def test_delete_nonexistent_habit(sample_data):
    with pytest.raises(ValueError) as exc:
        delete_habit(sample_data, "Reading")

    assert str(exc.value) == "Habit does not exist."


def test_delete_archived_habit_without_logs(sample_data):
    add_habit(sample_data, "Reading", 5)

    archive_habit(sample_data, "Reading")

    result = delete_habit(sample_data, "Reading")

    assert result == "Reading deleted."
    assert "Reading" not in sample_data["habits"]

    
def test_delete_habit_with_existing_logs_raises_error(sample_data):
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

    with pytest.raises(ValueError, match="existing logs"):
        delete_habit(sample_data, "Reading")

    assert "Reading" in sample_data["habits"]
    assert sample_data["logs"] == [
        {
            "habit": "Reading",
            "date": "2026-05-10"
        },
        {
            "habit": "Workout",
            "date": "2026-05-10"
        }
    ]


def test_delete_habit_with_multiple_logs_raises_error(sample_data):
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

    with pytest.raises(ValueError, match="existing logs"):
        delete_habit(sample_data, "Reading")

    assert "Reading" in sample_data["habits"]
    assert len(sample_data["logs"]) == 3


# rename_habit tests

def test_rename_habit_success(sample_data):
    add_habit(sample_data, "Workot", 5)
    log_habit(sample_data, "2026-05-10", "Workot")
    result = rename_habit(sample_data, "Workot", "Workout")

    assert "Workout" in sample_data["habits"]
    assert "Workot" not in sample_data["habits"]
    assert sample_data["logs"][0]["habit"] == "Workout"
    assert result == "Workot renamed to Workout."


def test_rename_nonexistent_habit(sample_data):
    with pytest.raises(ValueError, match="Habit does not exist."):
        rename_habit(sample_data, "Missing", "Workout")


def test_rename_habit_to_existing_habit(sample_data):
    add_habit(sample_data, "Workout", 5)
    add_habit(sample_data, "Reading", 3)

    with pytest.raises(ValueError, match="Habit already exists."):
        rename_habit(sample_data, "Workout", "Reading")


def test_rename_habit_invalid_new_name(sample_data):
    add_habit(sample_data, "Workout", 5)

    with pytest.raises(ValueError):
        rename_habit(sample_data, "Workout", "A")


# update_habit_target tests

def test_update_habit_target_success(sample_data):
    add_habit(sample_data, "Workout", 5)

    result = update_habit_target(sample_data, "Workout", 7)

    assert sample_data["habits"]["Workout"]["target_per_week"] == 7
    assert result == "Workout target updated to 7 per week."


def test_update_habit_target_nonexistent_habit(sample_data):
    with pytest.raises(ValueError, match="Habit does not exist."):
        update_habit_target(sample_data, "Workout", 7)


def test_update_habit_target_invalid_target(sample_data):
    add_habit(sample_data, "Workout", 5)

    with pytest.raises(ValueError):
        update_habit_target(sample_data, "Workout", 0)


def test_update_habit_target_invalid_habit_name(sample_data):
    with pytest.raises(ValueError):
        update_habit_target(sample_data, "A", 5)


def test_get_habit_logs_success(sample_data):
    add_habit(sample_data, "Workout", 5)
    sample_data["habits"]["Workout"]["created_at"] = "2026-04-01"
    log_habit(sample_data, "2026-05-10", "Workout")
    log_habit(sample_data, "2026-05-09", "Workout")

    assert get_habit_logs(sample_data, "Workout") == ["2026-05-10", "2026-05-09"]


def test_get_nonexistent_habit_logs(sample_data):
    with pytest.raises(ValueError, match="Habit does not exist."):
        get_habit_logs(sample_data, "Workout")


def test_get_habit_logs_no_logs(sample_data):
    add_habit(sample_data, "Workout", 5)

    assert get_habit_logs(sample_data, "Workout") == []


# update_habit_description tests

def test_update_habit_description_success(sample_data):
    add_habit(sample_data, "Workout", 5)
    result = update_habit_description(sample_data, "Workout", "Strength training")

    assert sample_data["habits"]["Workout"]["description"] == "Strength training"
    assert result == "Workout description updated."


def test_update_habit_description_clears_to_empty_string(sample_data):
    add_habit(sample_data, "Workout", 5)
    update_habit_description(sample_data, "Workout", "Strength training")
    result = update_habit_description(sample_data, "Workout", "")

    assert sample_data["habits"]["Workout"]["description"] == ""
    assert result == "Workout description updated."


def test_update_habit_description_nonexistent_habit(sample_data):

    with pytest.raises(ValueError, match="Habit does not exist."):
        update_habit_description(sample_data, "Workout", "Strength training")


def test_update_habit_description_invalid_habit_name(sample_data):

    with pytest.raises(ValueError, match="Minimum 3 characters required."):
        update_habit_description(sample_data, "A", "Strength training")


def test_update_habit_description_invalid_description(sample_data):
    add_habit(sample_data, "Workout", 5)

    with pytest.raises(ValueError, match="Input must be a string."):
        update_habit_description(sample_data, "Workout", 123)


def test_update_habit_description_rejects_none(sample_data):
    add_habit(sample_data, "Workout", 5)

    with pytest.raises(ValueError, match="Input must be a string."):
        update_habit_description(sample_data, "Workout", None)


def test_update_habit_description_rejects_list(sample_data):
    add_habit(sample_data, "Workout", 5)

    with pytest.raises(ValueError, match="Input must be a string."):
        update_habit_description(sample_data, "Workout", [1, 2, 3])


def test_update_habit_description_trims_whitespace(sample_data):
    add_habit(sample_data, "Reading", 5)
    result = update_habit_description(sample_data, "Reading", "   Read 10 pages daily   ")

    assert sample_data["habits"]["Reading"]["description"] == "Read 10 pages daily"
    assert result == "Reading description updated."

