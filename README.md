# Habit Tracker

A command-line habit tracker built in Python for tracking habits, daily progress, streaks, weekly targets, and recovery after missed days.

## Features

- Add habits with weekly targets
- Log habits by date
- View completed and pending habits for a selected date
- View habit logs
- Delete individual logs
- View habit details
- Archive and unarchive habits
- Permanently delete habits only when they have no logs
- View a daily dashboard with:
  - daily completion summary
  - completed habits
  - pending habits
  - previous-day missed habits
  - recovery hint after missed days
  - today's focus habits
  - weekly progress
- Track current streaks and best streaks
- Track weekly habit completion
- Safe JSON storage with validation and backups
- Tested with pytest

## Data Safety

The app validates the JSON data structure before loading and saving.

It checks that:

- every habit has the required fields
- every log has the required fields
- logs reference existing habits
- duplicate logs are rejected
- logs cannot exist before habit creation
- logs cannot exist after habit archive
- habits with logs cannot be permanently deleted
- backups are created before overwriting data

## Tech Used

- Python
- JSON storage
- datetime module
- pytest

## How to Run

1. Clone the repository
2. Run the app:

```bash
python main.py
```

## Project Structure

```txt
main.py          - CLI entry point and menu handlers
habits.py        - Core habit actions
stats.py         - Daily, weekly, and streak calculations
storage.py       - JSON loading, saving, migration, and backups
validators.py   - User input and data structure validation
helpers.py      - Display formatting and dashboard helper functions
utils.py         - Shared CLI utility functions
config.py        - Project configuration
tests/           - pytest test suite
```

## Testing

Run the test suite with:

```bash
pytest
```

The project includes tests for habit actions, validation, storage, statistics, helpers, utilities, and CLI handler behavior.

## Future Improvements

- SQLite database
- GUI / Web version
- Charts dashboard
- User accounts

## Example Data

This project does not include personal runtime data.

To try the app with sample data, copy:

data.example.json

and rename the copy to:

data.json