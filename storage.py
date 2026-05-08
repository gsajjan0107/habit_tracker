import json
import shutil
from datetime import datetime
from typing import Dict, Any
import logging
from validators import validate_data_structure
from config import DATA_FILE

def create_default_data():
    return {
        "habits": [],
        "logs": {}
    }

HabitData = dict[str, Any]

def create_data_file() -> HabitData:
    data = create_default_data()

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return data

def backup_and_reset() -> HabitData:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_file_path = DATA_FILE.with_name(f"data_backup_{timestamp}.json")

    n = 1
    while backup_file_path.exists():
        backup_file_path = DATA_FILE.with_name(f"data_backup_{timestamp}_{n}.json")
        n += 1

    if DATA_FILE.exists():
        DATA_FILE.rename(backup_file_path)

    return create_data_file()

def load_data() -> HabitData:

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        is_valid, msg = validate_data_structure(data) 
        if not is_valid:
            return backup_and_reset()
             
        return data

    except FileNotFoundError:
        return create_data_file()
    
    except json.JSONDecodeError:
        return backup_and_reset()
    
def create_backup() -> None:
    
    if DATA_FILE.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_file_path = DATA_FILE.with_name(f"data_backup_{timestamp}.json")
        shutil.copy(DATA_FILE, backup_file_path)

        backups = list(DATA_FILE.parent.glob("data_backup_*.json"))
        MAX_BACKUPS = 5

        if len(backups) > MAX_BACKUPS:
            backups.sort()
            for old_file in backups[:-MAX_BACKUPS]:
                old_file.unlink()

def save_data(data: Dict[str, Any]) -> None:

    is_valid, msg = validate_data_structure(data)

    if not is_valid:
        raise ValueError(f"Cannot save invalid data: {msg}")
    
    temp_path = DATA_FILE.with_suffix(".tmp")
    
    try:
        create_backup()

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        temp_path.replace(DATA_FILE)

    except Exception as e:

        if temp_path.exists():
            temp_path.unlink()

        raise RuntimeError(f"Failed to save data: {e}")