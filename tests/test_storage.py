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