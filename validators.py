from datetime import datetime
import re

def get_valid_input(prompt, validator):
    while True:
        value = input(prompt).strip()
        try:
            return validator(value)
        except ValueError as e:
            print(f"Error: {e}")

def validate_int(value, min_val=None, max_val=None):
    try:
        num = int(value)
    except ValueError:
        raise   ValueError("Must be a number.")
    
    if min_val is not None and num < min_val:
        raise ValueError(f"Must be >= {min_val}")
    
    if max_val is not None and num > max_val:
        raise ValueError(f"Must be <= {max_val}")
    
    return num

def validate_string(value, min_len=1, max_len=None):
    value = value.strip()

    if not value:
        raise ValueError("Cannot be empty.")
    
    if len(value) < min_len:
        raise ValueError(f"Minimum {min_len} characters required.")
    
    if max_len is not None and len(value) > max_len:
        raise ValueError(f"Maximum {max_len} characters allowed.")
    
    if not re.match(r"^[A-Za-z \-]+$", value):
        raise ValueError("Only letters and spaces allowed")
    
    return value.title()

def validate_choice(value, choices):
    value = value.strip().lower()

    if value not in choices:
        raise ValueError(f"Choose from {choices}")
    
    return value

def validate_date(value):
    value = value.strip()

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Use format YYYY-MM-DD (e.g., 2026-04-25)")