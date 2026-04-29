import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from validators import validate_int, validate_string, validate_choice, validate_date
from datetime import date

def test_validate_int():
    assert validate_int("5") == 5

def test_validate_string():
    assert validate_string("girish") == "Girish"

def test_validate_choice():
    assert validate_choice("yes", ["yes", "no"]) == "yes"

def test_validate_date():
    assert validate_date("2026-04-29") == date(2026, 4, 29)