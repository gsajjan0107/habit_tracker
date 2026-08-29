from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"

DEFAULT_SCHEDULED_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun",]
VALID_DAYS = frozenset(DEFAULT_SCHEDULED_DAYS)