import json
import tempfile
from pathlib import Path
from storage import load_habits, save_habits

class TestStorage:
    
    def test_load_habist_existing_file(self):
        test_data = {"exercise": ["2024-01-01", "2024-01-02"]}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name

        import storage
        original_path = storage.FILE_PATH
        storage.FILE_PATH = Path(temp_path)

        try:
            result = load_habits()
            assert result == test_data
        finally:
            storage.FILE_PATH = original_path
            Path(temp_path).unlink()

    def test_load_habits_missing_file(self):
        import storage
        original_path = storage.FILE_PATH
        storage.FILE_PATH = Path("nonexistent.json")

        try:
            result = load_habits()
            assert result == {}
        finally:
            storage.FILE_PATH = original_path

    def test_saving_habits(self):
        test_data = {"reading": ["2024-01-01"]}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        import storage
        original_path = storage.FILE_PATH
        storage.FILE_PATH = Path(temp_path)

        try:
            save_habits(test_data)
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            assert saved_data == test_data
        finally:
            storage.FILE_PATH = original_path
            Path(temp_path).unlink()