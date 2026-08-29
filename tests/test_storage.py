import json
import pytest
import storage
from config import DEFAULT_SCHEDULED_DAYS

def test_load_data_creates_file_if_missing(tmp_path, monkeypatch):
    # Redirect file path to isolated temp location
    test_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", test_file)

    # Ensure file does NOT exist
    assert not test_file.exists()

    data = storage.load_data()

    # file must now exist
    assert test_file.exists()

    # structure must be correct
    assert data["schema_version"] == 1
    assert "habits" in data
    assert "logs" in data
    assert isinstance(data["habits"], dict)
    assert isinstance(data["logs"], list)

def test_load_data_handles_invalid_json_creates_backup(tmp_path, monkeypatch):
    test_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", test_file)

    # create corrupted JSON
    test_file.write_text("{ broken json }")

    data = storage.load_data()

    # original file should be replaced by backup system
    assert test_file.exists()

    # verify system recovered structure
    assert data["schema_version"] == 1
    assert "habits" in data
    assert "logs" in data

    # now the important part → backup must exist
    backup_files = list(tmp_path.glob("data_backup_*.json"))
    assert len(backup_files) > 0


def test_save_data_writes_valid_data(tmp_path, monkeypatch):
    test_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", test_file)

    data = {
        "schema_version": 1,
        "habits": {
            "Workout": {
                "id": 1,
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
                "description": "",
                "scheduled_days": DEFAULT_SCHEDULED_DAYS.copy(),
            }
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
                "note": ""
            }
        ],
    }

    storage.save_data(data)

    saved_data = json.loads(test_file.read_text())

    assert saved_data == data


def test_save_data_rejects_invalid_data(tmp_path, monkeypatch):
    test_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", test_file)

    invalid_data = {
        "habits": {},
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }

    with pytest.raises(ValueError, match="Cannot save invalid data"):
        storage.save_data(invalid_data)


def test_save_data_does_not_overwrite_existing_file_when_data_is_invalid(tmp_path, monkeypatch):
    test_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", test_file)

    existing_data = {
        "schema_version": 1,
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
                "description": ""
            }
        },
        "logs": [],
    }

    test_file.write_text(json.dumps(existing_data, indent=4))

    invalid_data = {
        "habits": {},
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }

    with pytest.raises(ValueError):
        storage.save_data(invalid_data)

    saved_data = json.loads(test_file.read_text())

    assert saved_data == existing_data


def test_save_data_creates_backup_before_overwriting_existing_file(tmp_path, monkeypatch):
    test_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", test_file)

    existing_data = {
        "schema_version": 1,
        "habits": {
            "Workout": {
                "id": 1,
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
                "description": "",
                "scheduled_days": DEFAULT_SCHEDULED_DAYS.copy(),
            }
        },
        "logs": [],
    }

    new_data = {
        "schema_version": 1,
        "habits": {
            "Workout": {
                "id": 1,
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
                "description": "",
                "scheduled_days": DEFAULT_SCHEDULED_DAYS.copy(),
            },
            "Reading": {
                "id": 2,
                "target_per_week": 3,
                "created_at": "2026-05-02",
                "archived_at": None,
                "description": "",
                "scheduled_days": DEFAULT_SCHEDULED_DAYS.copy(),
            },
        },
        "logs": [],
    }

    test_file.write_text(json.dumps(existing_data, indent=4))

    storage.save_data(new_data)

    backup_files = list(tmp_path.glob("data_backup_*.json"))

    assert len(backup_files) == 1

    backup_data = json.loads(backup_files[0].read_text())
    saved_data = json.loads(test_file.read_text())

    assert backup_data == existing_data
    assert saved_data == new_data


def test_save_data_does_not_create_backup_when_file_does_not_exist(tmp_path, monkeypatch):
    test_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", test_file)

    data = {
        "schema_version": 1,
        "habits": {
            "Workout": {
                "id": 1,
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
                "description": "",
                "scheduled_days": DEFAULT_SCHEDULED_DAYS.copy(),
            }
        },
        "logs": [],
    }

    storage.save_data(data)

    saved_data = json.loads(test_file.read_text())
    backup_files = list(tmp_path.glob("data_backup_*.json"))

    assert saved_data == data
    assert backup_files == []


def test_migrate_data_adds_schema_version_to_old_data():
    data = {
        "habits": {},
        "logs": []
    }

    result, was_migrated = storage.migrate_data(data)

    assert result["schema_version"] == 1
    assert was_migrated is True


def test_migrate_data_preserves_existing_schema_version():
    data = {
        "schema_version": 1,
        "habits": {},
        "logs": []
    }

    result, was_migrated = storage.migrate_data(data)

    assert result["schema_version"] == 1
    assert was_migrated is False


def test_load_data_accepts_old_data(tmp_path, monkeypatch):
    test_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", test_file)

    data = {
        "habits": {},
        "logs": []
    }

    test_file.write_text(json.dumps(data, indent=4))
    data = storage.load_data()

    assert data["schema_version"] == 1


def test_migrate_data_returns_non_dict_unchanged():
    data = ["not", "a", "dict"]

    result, was_migrated = storage.migrate_data(data)

    assert result == data
    assert was_migrated is False


def test_migrate_data_preserves_old_data_content():
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
                "description": ""
            }
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }

    result, was_migrated = storage.migrate_data(data)

    assert result["schema_version"] == 1
    assert result["habits"] == data["habits"]
    assert result["logs"] == data["logs"]


def test_load_data_saves_migrated_old_data(tmp_path, monkeypatch):
    test_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", test_file)

    old_data = {
        "habits": {},
        "logs": [],
    }

    test_file.write_text(json.dumps(old_data, indent=4))

    data = storage.load_data()
    saved_data = json.loads(test_file.read_text())

    assert data["schema_version"] == 1
    assert saved_data["schema_version"] == 1


def test_load_data_handles_invalid_structure_creates_backup(tmp_path, monkeypatch):
    test_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", test_file)

    invalid_data = {
        "schema_version": 1,
        "habits": [],
        "logs": [],
    }

    test_file.write_text(json.dumps(invalid_data, indent=4))

    data = storage.load_data()

    backup_files = list(tmp_path.glob("data_backup_*.json"))

    assert test_file.exists()
    assert len(backup_files) == 1

    assert data["schema_version"] == 1
    assert data["habits"] == {}
    assert data["logs"] == []

    backup_data = json.loads(backup_files[0].read_text())
    assert backup_data == invalid_data


def test_migrate_data_adds_missing_description_to_existing_habits():
    data = {
        "schema_version": 1,
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [],
    }

    result, was_migrated = storage.migrate_data(data)

    assert result["habits"]["Workout"]["description"] == ""
    assert was_migrated is True


def test_migrate_data_does_not_change_habits_that_already_have_description():
    data = {
        "schema_version": 1,
        "habits": {
            "Workout": {
                "id": 1,
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
                "description": "Strength training",
                "scheduled_days": DEFAULT_SCHEDULED_DAYS.copy(),
            }
        },
        "logs": [],
    }

    result, was_migrated = storage.migrate_data(data)

    assert result["habits"]["Workout"]["description"] == "Strength training"
    assert was_migrated is False


def test_migrate_data_adds_missing_scheduled_days_to_existing_habits():
    data = {
        "schema_version": 1,
        "habits": {
            "Workout": {
                "id": 1,
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
                "description": "",
            }
        },
        "logs": [],
    }

    result, was_migrated = storage.migrate_data(data)

    assert result["habits"]["Workout"]["scheduled_days"] == DEFAULT_SCHEDULED_DAYS
    assert was_migrated is True