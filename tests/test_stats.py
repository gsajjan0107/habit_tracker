import pytest
from stats import daily_stats, streaks
from habits import add_habit, log_habit


def test_daily_stats_no_habits(sample_data):
    with pytest.raises(ValueError, match="No habits created."):
        daily_stats(sample_data, "2026-05-10")


def test_daily_stats_invalid_date(sample_data):
    add_habit(sample_data, "Workout", 5)

    with pytest.raises(ValueError):
        daily_stats(sample_data, "invalid-date")


def test_daily_stats_completed_and_pending(sample_data):
    add_habit(sample_data, "Workout", 5)
    add_habit(sample_data, "Reading", 3)

    log_habit(sample_data, "2026-05-10", "Workout")

    result = daily_stats(sample_data, "2026-05-10")

    assert result["completed"] == ["Workout"]
    assert result["pending"] == ["Reading"]

    assert result["total_completed"] == 1
    assert result["total_habits"] == 2

    assert result["completion_rate"] == 50.0


def test_daily_stats_excludes_archived_habits(sample_data):
    add_habit(sample_data, "Workout", 5)
    add_habit(sample_data, "Reading", 3)

    sample_data["habits"]["Reading"]["archived_at"] = "2026-05-09"

    result = daily_stats(sample_data)

    assert "Reading" not in result["completed"]
    assert "Reading" not in result["pending"]

    assert result["total_habits"] == 1


def test_daily_stats_excludes_future_created_habits(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2026-05-10",
        "archived_at": None
    }
    
    result = daily_stats(sample_data, "2026-05-09")

    assert result["date"] == "2026-05-09"
    assert result["completed"] == []
    assert result["pending"] == []
    assert result["total_completed"] == 0
    assert result["total_habits"] == 0
    assert result["completion_rate"] == 0


def test_daily_stats_archived_after_date_still_valid(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2026-05-01",
        "archived_at": "2026-05-10"
    }

    result = daily_stats(sample_data, "2026-05-08")

    assert result["total_habits"] == 1


def test_daily_stats_archived_before_date_excluded(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2026-05-01",
        "archived_at": "2026-05-05"
    }
    
    result = daily_stats(sample_data, "2026-05-10")

    assert result["date"] == "2026-05-10"
    assert result["completed"] == []
    assert result["pending"] == []
    assert result["total_completed"] == 0
    assert result["total_habits"] == 0
    assert result["completion_rate"] == 0


def test_daily_stats_completed_sorted(sample_data):
    add_habit(sample_data, "Reading", 3)
    add_habit(sample_data, "Workout", 5)

    log_habit(sample_data, "2026-05-10", "Workout")
    log_habit(sample_data, "2026-05-10", "Reading")

    result = daily_stats(sample_data, "2026-05-10")

    assert result["completed"] == ["Reading", "Workout"]


def test_streaks_defaults_to_today(sample_data):
    add_habit(sample_data, "Workout", 5)
    log_habit(sample_data, None, "Workout")

    result = streaks(sample_data)

    assert "Workout" in result
    assert result["Workout"]["current_streak"] == 1
    assert result["Workout"]["longest_streak"] == 1


def test_streaks_excludes_future_created_habits(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2026-05-10",
        "archived_at": None
    }

    sample_data["logs"].append({
        "habit": "Workout",
        "date": "2026-05-10"
    })

    result = streaks(sample_data, "2026-05-09")

    assert "Workout" not in result


def test_streaks_excludes_archived_before_selected_date(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2026-05-01",
        "archived_at": "2026-05-05"
    }

    sample_data["logs"].append({
        "habit": "Workout",
        "date": "2026-05-04"
    })

    result = streaks(sample_data, "2026-05-10")

    assert "Workout" not in result


def test_streaks_with_habits_but_no_logs(sample_data):
    add_habit(sample_data, "Workout", 5)

    result = streaks(sample_data, "2026-05-10")

    assert result["Workout"]["current_streak"] == 0
    assert result["Workout"]["longest_streak"] == 0


def test_daily_stats_before_any_habit_is_valid(sample_data):
    add_habit(sample_data, "Workout", 5)

    result = daily_stats(sample_data, "2026-05-01")

    assert result["date"] == "2026-05-01"
    assert result["completed"] == []
    assert result["pending"] == []
    assert result["total_completed"] == 0
    assert result["total_habits"] == 0
    assert result["completion_rate"] == 0