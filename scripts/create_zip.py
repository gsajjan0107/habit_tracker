from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FOLDER = PROJECT_ROOT / "zips"

FILES_TO_ZIP = [
    "config.py",
    "main.py",
    "habits.py",
    "stats.py",
    "storage.py",
    "validators.py",
    "helpers.py",
    "utils.py",
    "tests/conftest.py",
    "tests/test_main.py",
    "tests/test_habits.py",
    "tests/test_stats.py",
    "tests/test_storage.py",
    "tests/test_validators.py",
    "tests/test_helpers.py",
    "tests/test_utils.py",
    "README.md",
    "requirements.txt",
    "data.example.json",
    "LICENSE",
    "pytest.ini",
]


def create_zip():
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    zip_path = OUTPUT_FOLDER / "habit_tracker.zip"
    missing_files = []

    with ZipFile(zip_path, "w", ZIP_DEFLATED) as zip_file:
        for file_name in FILES_TO_ZIP:
            file_path = PROJECT_ROOT / file_name

            if file_path.exists():
                zip_file.write(file_path, arcname=file_name)
                print(f"Added: {file_name}")
            else:
                missing_files.append(file_name)

    if missing_files:
        print("\nMissing files:")
        for file_name in missing_files:
            print(f"- {file_name}")

    print(f"\nCreated/updated zip: {zip_path}")


if __name__ == "__main__":
    create_zip()