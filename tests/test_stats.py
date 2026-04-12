"""
Tests for stats.py.

Why mock `date.today()`?
Your streak and rolling-window logic depend on "today". In a test, real "today"
changes every day, so the same code would give different results on Tuesday vs
Wednesday. We replace `date.today()` with a fixed day so tests are repeatable.
"""

from datetime import date, timedelta
from unittest.mock import patch

import pytest

from stats import longest_streak, repetitions, streak, times_done


# Fixed "today" for deterministic tests (Sunday 12 Apr 2026 per your session date)
TODAY = date(2026, 4, 12)


@pytest.fixture
def fake_today():
    """Replace `stats.date` so `date.today()` is fixed (Python 3.14+ blocks patching `date.today` on the real class)."""
    with patch("stats.date") as mock_date:
        mock_date.today.return_value = TODAY
        yield mock_date


def test_streak_includes_today_when_marked(fake_today):
    logs = {"run": [TODAY.isoformat(), (TODAY - timedelta(days=1)).isoformat()]}
    assert streak("run", logs) == 2


def test_streak_starts_from_yesterday_if_not_done_today(fake_today):
    """If you skipped today but did yesterday, streak counts from yesterday backward."""
    logs = {"run": [(TODAY - timedelta(days=1)).isoformat()]}
    assert streak("run", logs) == 1


def test_streak_zero_when_no_recent_days(fake_today):
    logs = {"run": [(TODAY - timedelta(days=5)).isoformat()]}
    assert streak("run", logs) == 0


def test_longest_streak_empty():
    assert longest_streak("x", {"x": []}) == 0


def test_longest_streak_single_day():
    assert longest_streak("x", {"x": ["2026-04-01"]}) == 1


def test_longest_streak_consecutive_block():
    logs = {
        "x": [
            "2026-04-01",
            "2026-04-02",
            "2026-04-03",
            "2026-04-10",
        ]
    }
    assert longest_streak("x", logs) == 3


def test_times_done_counts_window(fake_today):
    """Last 7 calendar days ending at 'today' (or yesterday if today not logged)."""
    days = [TODAY - timedelta(days=i) for i in range(3)]
    logs = {"run": [d.isoformat() for d in days]}
    assert times_done("run", 7, logs) == 3


def test_repetitions_is_length():
    logs = {"run": ["2026-01-01", "2026-01-02"]}
    assert repetitions("run", logs) == 2
