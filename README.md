# Habit Tracker

A command-line habit tracker built in Python for tracking habits, daily progress, streaks, weekly targets, and recovery after missed days.

## Project Status

This project is a stable and tested command-line habit tracker. It supports habit creation, logging, archived habits, detailed habit insights, dashboard summaries, JSON validation, backups, and automated tests.

## Features

- Add habits with weekly targets
- Log habits by date
- View completed and pending habits for a selected date
- View habit logs
- Delete individual logs
- View detailed habit insights, including habit age, total logs, average logs per week, consistency rating, streaks, weekly progress, last logged date, and archived status
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

## CLI Usage Notes

- Press Enter at date prompts to use today's date.
- Type `q` at supported prompts to cancel the current action.
- Cancel input is case-insensitive, so both `q` and `Q` work.

## Example Habit Details Output

```txt
==== HABIT DETAILS ====

Habit: Workout
Target: 5 per week
Created: Friday, 01 May 2026
Habit age: 9 days
Status: Archived
Total logs: 6
Average logs per week: 4.20
Consistency: 60.00% - Good
Last logged: Sunday, 10 May 2026
Days since last log: 0 days
Current streak: 3 days
Best streak: 5 days
This week: 3/5 completed (60.00%) - ⚠️ You can still recover. 4 days left.
Remaining this week: 2
Archived: Sunday, 10 May 2026
```

## Key Learning Outcomes

This project demonstrates:

- modular Python project structure
- command-line input handling
- date-based habit tracking logic
- JSON data validation and migration
- backup-safe file storage
- pytest-based unit and handler testing
- refactoring large CLI handlers into focused helper functions

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

The project currently has 343 passing tests covering habit actions, validation, storage, statistics, helpers, utilities, and CLI handler behavior.

## Limitations

- Data is stored locally in JSON files, not a database
- The app is designed for single-user command-line use
- There is no graphical interface yet
- Charts and long-term trend visualizations are planned but not implemented

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