from utils import build_archive_menu_entries

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