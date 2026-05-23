import pytest
from stats import daily_stats, streaks, habit_weekly_completion
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


def test_habit_weekly_completion_counts_logs_in_selected_week(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2026-05-01",
        "archived_at": None
    }

    sample_data["logs"].extend([
        {"habit": "Workout", "date": "2026-05-04"},
        {"habit": "Workout", "date": "2026-05-05"},
        {"habit": "Workout", "date": "2026-05-10"},
    ])

    result = habit_weekly_completion(sample_data, "2026-05-10")

    assert result["Workout"]["done"] == 3
    assert result["Workout"]["target"] == 5
    assert result["Workout"]["percentage"] == 60.0


def test_habit_weekly_completion_percentage_capped_at_100(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 2,
        "created_at": "2026-05-01",
        "archived_at": None
    }

    sample_data["logs"].extend([
        {"habit": "Workout", "date": "2026-05-04"},
        {"habit": "Workout", "date": "2026-05-05"},
        {"habit": "Workout", "date": "2026-05-06"},
    ])

    result = habit_weekly_completion(sample_data, "2026-05-10")

    assert result["Workout"]["done"] == 3
    assert result["Workout"]["target"] == 2
    assert result["Workout"]["percentage"] == 100


def test_habit_weekly_completion_ignores_logs_outside_selected_week(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2020-05-01",
        "archived_at": None
    }

    sample_data["logs"].extend([
        {"habit": "Workout", "date": "2020-05-03"},  # previous week
        {"habit": "Workout", "date": "2020-05-04"},  # selected week
        {"habit": "Workout", "date": "2020-05-10"},  # selected week
        {"habit": "Workout", "date": "2020-05-11"},  # next week
    ])

    result = habit_weekly_completion(sample_data, "2020-05-10")

    assert result["Workout"]["done"] == 2
    assert result["Workout"]["target"] == 5
    assert result["Workout"]["percentage"] == 40.0


def test_streaks_calculates_current_and_longest_streak(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2020-05-01",
        "archived_at": None
    }

    sample_data["logs"].extend([
        {"habit": "Workout", "date": "2020-05-01"},
        {"habit": "Workout", "date": "2020-05-02"},
        {"habit": "Workout", "date": "2020-05-04"},
        {"habit": "Workout", "date": "2020-05-05"},
        {"habit": "Workout", "date": "2020-05-06"},
    ])

    result = streaks(sample_data, "2020-05-06")

    assert result["Workout"]["current_streak"] == 3
    assert result["Workout"]["longest_streak"] == 3


def test_streaks_current_streak_zero_when_selected_date_not_logged(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2020-05-01",
        "archived_at": None
    }

    sample_data["logs"].extend([
        {"habit": "Workout", "date": "2020-05-01"},
        {"habit": "Workout", "date": "2020-05-02"},
        {"habit": "Workout", "date": "2020-05-03"},
    ])

    result = streaks(sample_data, "2020-05-05")

    assert result["Workout"]["current_streak"] == 0
    assert result["Workout"]["longest_streak"] == 3


def test_habit_weekly_completion_excludes_habit_created_after_week(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2020-05-11",
        "archived_at": None
    }

    result = habit_weekly_completion(sample_data, "2020-05-10")

    assert "Workout" not in result


def test_habit_weekly_completion_excludes_habit_archived_before_week(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2020-05-01",
        "archived_at": "2020-05-03"
    }

    result = habit_weekly_completion(sample_data, "2020-05-10")

    assert "Workout" not in result


def test_habit_weekly_completion_includes_habit_created_during_week(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2020-05-06",
        "archived_at": None
    }

    sample_data["logs"].append({
        "habit": "Workout",
        "date": "2020-05-06"
    })

    result = habit_weekly_completion(sample_data, "2020-05-10")

    assert "Workout" in result
    assert result["Workout"]["done"] == 1
    assert result["Workout"]["target"] == 5
    assert result["Workout"]["percentage"] == 20.0


def test_habit_weekly_completion_includes_habit_archived_during_week(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2020-05-01",
        "archived_at": "2020-05-06"
    }

    sample_data["logs"].append({
        "habit": "Workout",
        "date": "2020-05-05"
    })

    result = habit_weekly_completion(sample_data, "2020-05-10")

    assert "Workout" in result
    assert result["Workout"]["done"] == 1
    assert result["Workout"]["target"] == 3
    assert result["Workout"]["percentage"] == 33.33


def test_habit_weekly_completion_adjusts_target_for_habit_created_during_week(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2020-05-09",
        "archived_at": None
    }

    sample_data["logs"].append({
        "habit": "Workout",
        "date": "2020-05-09"
    })

    result = habit_weekly_completion(sample_data, "2020-05-10")

    assert result["Workout"]["done"] == 1
    assert result["Workout"]["target"] == 2
    assert result["Workout"]["percentage"] == 50.0


def test_habit_weekly_completion_adjusts_target_for_habit_archived_during_week(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2020-05-01",
        "archived_at": "2020-05-05"
    }

    sample_data["logs"].append({
        "habit": "Workout",
        "date": "2020-05-04"
    })

    result = habit_weekly_completion(sample_data, "2020-05-10")

    assert result["Workout"]["done"] == 1
    assert result["Workout"]["target"] == 2
    assert result["Workout"]["percentage"] == 50.0


def test_habit_weekly_completion_counts_each_habit_separately(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2020-05-01",
        "archived_at": None
    }

    sample_data["habits"]["Reading"] = {
        "target_per_week": 3,
        "created_at": "2020-05-01",
        "archived_at": None
    }

    sample_data["logs"].extend([
        {"habit": "Workout", "date": "2020-05-04"},
        {"habit": "Workout", "date": "2020-05-05"},
        {"habit": "Reading", "date": "2020-05-04"},
    ])

    result = habit_weekly_completion(sample_data, "2020-05-10")

    assert result["Workout"]["done"] == 2
    assert result["Workout"]["target"] == 5
    assert result["Workout"]["percentage"] == 40.0

    assert result["Reading"]["done"] == 1
    assert result["Reading"]["target"] == 3
    assert result["Reading"]["percentage"] == 33.33


def test_daily_stats_pending_sorted(sample_data):
    add_habit(sample_data, "Workout", 5)
    add_habit(sample_data, "Reading", 3)
    add_habit(sample_data, "Boxing", 4)

    result = daily_stats(sample_data, "2026-05-10")

    assert result["pending"] == ["Boxing", "Reading", "Workout"]


def test_daily_stats_ignores_logs_for_archived_habit_after_archive_date(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2020-05-01",
        "archived_at": "2020-05-05"
    }

    sample_data["logs"].append({
        "habit": "Workout",
        "date": "2020-05-10"
    })

    result = daily_stats(sample_data, "2020-05-10")

    assert result["completed"] == []
    assert result["pending"] == []
    assert result["total_habits"] == 0
    assert result["total_completed"] == 0
    assert result["completion_rate"] == 0


def test_daily_stats_ignores_logs_before_habit_creation(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2020-05-10",
        "archived_at": None
    }

    sample_data["logs"].append({
        "habit": "Workout",
        "date": "2020-05-05"
    })

    result = daily_stats(sample_data, "2020-05-05")

    assert result["completed"] == []
    assert result["pending"] == []
    assert result["total_habits"] == 0
    assert result["total_completed"] == 0
    assert result["completion_rate"] == 0


def test_streaks_includes_habit_on_archive_date(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2020-05-01",
        "archived_at": "2020-05-05"
    }

    sample_data["logs"].extend([
        {"habit": "Workout", "date": "2020-05-04"},
        {"habit": "Workout", "date": "2020-05-05"},
    ])

    result = streaks(sample_data, "2020-05-05")

    assert "Workout" in result
    assert result["Workout"]["current_streak"] == 2
    assert result["Workout"]["longest_streak"] == 2


def test_streaks_includes_habit_on_creation_date(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 5,
        "created_at": "2020-05-05",
        "archived_at": None
    }

    sample_data["logs"].append({
        "habit": "Workout",
        "date": "2020-05-05"
    })

    result = streaks(sample_data, "2020-05-05")

    assert "Workout" in result
    assert result["Workout"]["current_streak"] == 1
    assert result["Workout"]["longest_streak"] == 1


def test_habit_weekly_completion_status_not_started(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 3,
        "created_at": "2020-05-01",
        "archived_at": None,
    }

    result = habit_weekly_completion(sample_data, "2020-05-06")

    assert result["Workout"]["status"] == "not_started"


def test_habit_weekly_completion_status_in_progress(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 3,
        "created_at": "2020-05-01",
        "archived_at": None,
    }

    sample_data["logs"].append({
        "habit": "Workout",
        "date": "2020-05-05",
    })

    result = habit_weekly_completion(sample_data, "2020-05-06")

    assert result["Workout"]["status"] == "in_progress"


def test_habit_weekly_completion_status_completed(sample_data):
    sample_data["habits"]["Workout"] = {
        "target_per_week": 3,
        "created_at": "2020-05-01",
        "archived_at": None,
    }

    sample_data["logs"].extend([
        {"habit": "Workout", "date": "2020-05-04"},
        {"habit": "Workout", "date": "2020-05-05"},
        {"habit": "Workout", "date": "2020-05-06"},
    ])

    result = habit_weekly_completion(sample_data, "2020-05-06")

    assert result["Workout"]["status"] == "completed"


