import pytest
from unittest.mock import patch
from datetime import datetime, date

from validators import validate_data_structure, get_valid_input, validate_int, validate_string, validate_choice, validate_date

# validate_int tests

def test_validate_int():
    assert validate_int("5") == 5

def test_validate_int_invalid():
    with pytest.raises(ValueError):
        validate_int("abc")

def test_validate_int_min_limit():
    assert validate_int("5", min_val=5) == 5

def test_validate_int_max_limit():
    assert validate_int("10", max_val=10) == 10

def test_validate_int_below_min():
    with pytest.raises(ValueError):
        validate_int("4", min_val=5)

def test_validate_int_above_max():
    with pytest.raises(ValueError):
        validate_int("11", max_val=10)

def test_get_valid_input_returns_validated_value():
    with patch("builtins.input", return_value="5"):
        result = get_valid_input("Enter number: ", validate_int)
        assert result == 5

def test_get_valid_input_retries_until_valid():
    with patch("builtins.input", side_effect=["abc", "5"]):
        result = get_valid_input("Enter number: ", validate_int)
        assert result == 5

def test_get_valid_input_prints_error():
    with patch("builtins.input", side_effect=["abc", "5"]), \
         patch("builtins.print") as mock_print:

        get_valid_input("Enter number: ", validate_int)

        mock_print.assert_called_with("Error: Input must be an integer.")

# validate_string tests

def test_validate_string():
    assert validate_string("girish") == "Girish"

def test_validate_string_empty():
    with pytest.raises(ValueError):
        validate_string("")

def test_validate_string_min_length():
    assert validate_string("Hi", min_len=2) == "Hi"

def test_validate_string_below_min():
    with pytest.raises(ValueError):
        validate_string("A", min_len=2)

def test_validate_string_max_length():
    assert validate_string("Cat", max_len=3) == "Cat"

def test_validate_string_above_max():
    with pytest.raises(ValueError):
        validate_string("Hello", max_len=3)

def test_validate_string_invalid_characters():
    with pytest.raises(ValueError):
        validate_string("Girish123")

# validate_choice tests

def test_validate_choice():
    assert validate_choice("yes", ["yes", "no"]) == "yes"

def test_validate_choice_invalid():
    with pytest.raises(ValueError):
        validate_choice("maybe", ["yes", "no"])

def test_validate_choice_strips_spaces():
    assert validate_choice(" yes ", ["yes", "no"]) == "yes"

def test_validate_choice_case_insensitive():
    assert validate_choice("YES", ["yes", "no"]) == "yes"

def test_validate_choice_empty():
    with pytest.raises(ValueError):
        validate_choice("", ["yes", "no"])

# validate_date tests

def test_validate_date():
    assert validate_date("2026-04-29") == date(2026, 4, 29)

def test_validate_date_invalid():
    with pytest.raises(ValueError):
        validate_date("29-04-2026")

def test_validate_date_existing_date_object():
    d = date(2026, 4, 29)
    assert validate_date(d) == d

def test_validate_date_invalid_month():
    with pytest.raises(ValueError):
        validate_date("2026-13-01")

def test_validate_date_invalid_day():
    with pytest.raises(ValueError):
        validate_date("2026-04-32")

def test_validate_date_empty():
    result = validate_date("")
    assert result == datetime.now().date()

def test_validate_date_non_string_input():
    with pytest.raises(ValueError):
        validate_date(123)

def test_validate_date_false_input():
    with pytest.raises(ValueError):
        validate_date(False)

def test_validate_data_structure_missing_target_per_week():
    data = {
        "habits": {
            "Workout": {
                "created_at": "2026-05-01",
                "archived_at": None
            }
        },
        "logs": []
    }

    success, msg = validate_data_structure(data)

    assert success is False
    assert "target_per_week" in msg
    assert "missing key" in msg


def test_validate_data_structure_missing_created_at():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "archived_at": None
            }
        },
        "logs": []
    }

    success, msg = validate_data_structure(data)

    assert success is False
    assert "created_at" in msg
    assert "missing key" in msg

def test_validate_data_structure_missing_log_date():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None
            }
        },
        "logs": [
            {
                "habit": "Workout"
            }
        ]
    }

    success, msg = validate_data_structure(data)

    assert success is False
    assert "logs[0].date" in msg
    assert "missing key" in msg

def test_validate_data_structure_missing_log_habit():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None
            }
        },
        "logs": [
            {
                "date": "2026-05-01"
            }
        ]
    }

    success, msg = validate_data_structure(data)

    assert success is False
    assert "logs[0].habit" in msg
    assert "missing key" in msg

def test_validate_data_structure_log_entry_not_dict():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None
            }
        },
        "logs": [
            "bad-log-entry"
        ]
    }

    success, msg = validate_data_structure(data)

    assert success is False
    assert "logs[0]" in msg
    assert "expected dict" in msg


def test_validate_data_structure_log_after_archive_date():
    data = {
        "habits": {
            "Reading": {
                "target_per_week": 5,
                "created_at": "2020-05-01",
                "archived_at": "2020-05-10",
            }
        },
        "logs": [
            {
                "habit": "Reading",
                "date": "2020-05-11",
            }
        ],
    }

    success, msg = validate_data_structure(data)

    assert success is False
    assert "logs[0]" in msg
    assert "date after habit archive" in msg


def test_validate_data_structure_active_habit_log_success():
    data = {
        "habits": {
            "Reading": {
                "target_per_week": 5,
                "created_at": "2020-05-01",
                "archived_at": None,
            }
        },
        "logs": [
            {
                "habit": "Reading",
                "date": "2020-05-02",
            }
        ],
    }

    success, msg = validate_data_structure(data)

    assert success is True
    assert msg is None
    

def test_validate_data_structure_missing_archived_at():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01"
            }
        },
        "logs": []
    }

    success, msg = validate_data_structure(data)

    assert success is False
    assert "archived_at" in msg


def test_validate_data_structure_log_references_missing_habit():
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
                "habit": "Reading",
                "date": "2026-05-01",
            }
        ],
    }

    success, msg = validate_data_structure(data)

    assert success is False
    assert "does not exist" in msg


def test_validate_data_structure_habit_with_extra_key_fails():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
                "wrong_key": None,
            }
        },
        "logs": [],
    }

    success, msg = validate_data_structure(data)

    assert success is False
    assert "invalid keys" in msg


def test_validate_data_structure_log_with_extra_key_fails():
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
                "wrong_key": "oops",
            }
        ],
    }

    success, msg = validate_data_structure(data)

    assert success is False
    assert "invalid keys" in msg