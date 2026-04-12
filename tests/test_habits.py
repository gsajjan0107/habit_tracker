import pytest
from habits import add_habit, delete_habit, rename_habit, mark_habit_done

class TestHabits:
    @pytest.fixture
    def sample_logs(self):
        return {
            "exercise": ["2024-01-01", "2024-01-02"],
            "reading": ["2024-01-01"]
        }
    
    def test_add_habit_success(self, sample_logs):
        add_habit("meditation", sample_logs)
        assert "meditation" in sample_logs
        assert sample_logs["meditation"] == []

    def test_add_habit_empty_name(self, sample_logs, capsys):
        add_habit("", sample_logs)
        captured = capsys.readouterr()
        assert "Habit cannot be empty" in captured.out
        assert len(sample_logs) == 2

    def test_add_habit_duplicate(self, sample_logs, capsys):
        add_habit("exercise", sample_logs)
        captured = capsys.readouterr()
        assert "already exists" in captured.out

    def test_delete_habit_success(self, sample_logs, capsys):
        delete_habit("exercise", sample_logs)
        captured = capsys.readouterr()
        assert "deleted" in captured.out
        assert "exercise" not in sample_logs

    def test_delete_habit_not_found(self, sample_logs, capsys):
        delete_habit("nonexistent", sample_logs)
        captured = capsys.readouterr()
        assert "does not exist" in captured.out

    def test_rename_habit_success(self, sample_logs, capsys):
        rename_habit("exercise", "workout", sample_logs)
        captured = capsys.readouterr()
        assert "renamed to" in captured.out
        assert "workout" in sample_logs
        assert "exercise" not in sample_logs

    def test_rename_habit_empty_name(self, sample_logs, capsys):
        rename_habit("exercise", "", sample_logs)
        captured = capsys.readouterr()
        assert "cannot be" in captured.out

    def test_mark_habit_done_new_day(self, sample_logs, capsys, monkeypatch):
        from datetime import date
        monkeypatch.setatte('habits.date', type('MockDate', (), {'today': lambda: date(2024, 1, 1)})())
        mark_habit_done("exercise", sample_logs)
        captured = capsys.readouterr()
        assert "already marked" in captured.out
        