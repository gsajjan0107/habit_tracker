from datetime import date
import pytest
import validators
import habits
import helpers


@pytest.fixture
def frozen_today(monkeypatch):
    fixed_today = date(2026, 5, 10)

    monkeypatch.setattr(helpers, "get_today", lambda: fixed_today)
    monkeypatch.setattr(habits, "get_today", lambda: fixed_today)
    monkeypatch.setattr(validators, "get_today", lambda: fixed_today)

    return fixed_today


@pytest.fixture
def sample_data(frozen_today):
    return {
        "habits": {},
        "logs": []
    }