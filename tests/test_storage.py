import json
import pytest
import storage

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
    assert "habits" in data
    assert "logs" in data

    # now the important part → backup must exist
    backup_files = list(tmp_path.glob("data_backup_*.json"))
    assert len(backup_files) > 0


def test_save_data_writes_valid_data(tmp_path, monkeypatch):
    test_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", test_file)

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
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
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
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [],
    }

    new_data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
            "Reading": {
                "target_per_week": 3,
                "created_at": "2026-05-02",
                "archived_at": None,
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
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [],
    }

    storage.save_data(data)

    saved_data = json.loads(test_file.read_text())
    backup_files = list(tmp_path.glob("data_backup_*.json"))

    assert saved_data == data
    assert backup_files == []


