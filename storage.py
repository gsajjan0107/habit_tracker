import json
from pathlib import Path
from datetime import datetime
from validation import validate_data_structure

file_path = Path(__file__).with_name("data.json")

def get_default_data():
    return {"habits": {}, "logs": []}

def create_data_file():
    data = get_default_data()

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return data

def backup_and_reset():
    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d_%H-%M-%S")

    base = f"data_backup_{formatted_now}"
    backup_file_path = file_path.with_name(f"{base}.json")

    n = 1
    while backup_file_path.exists():
        backup_file_path = file_path.with_name(f"{base}_{n}.json")
        n += 1

    if file_path.exists():
        file_path.rename(backup_file_path)

    return create_data_file()

def load_data():

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not validate_data_structure(data):
            return backup_and_reset()
        
        return data

    except FileNotFoundError:
        return create_data_file()
    
    except json.JSONDecodeError:
        return backup_and_reset()

def save_data(data):
    temp_path = file_path.with_suffix(".tmp")

    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    temp_path.replace(file_path)
