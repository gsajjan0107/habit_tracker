from pathlib import Path
import storage

def test_load_data_creates_file_if_missing(tmp_path, monkeypatch):
    # Redirect file path to isolated temp location
    test_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "file_path", test_file)

    # Ensure file does NOT exist
    assert not test_file.exists()

    data, msg = storage.load_data()

    # file must now exist
    assert test_file.exists()

    # structure must be correct
    assert "habits" in data
    assert "logs" in data
    assert isinstance(data["habits"], dict)
    assert isinstance(data["logs"], list)

    # sanity check message
    assert "Created new data file" in msg