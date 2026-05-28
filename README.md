# Habit Tracker

A command-line habit tracking app built in Python to track daily habits, streaks, and progress.

## Features

- Add habits with weekly targets
- Log habits by date
- View habit logs
- Delete individual logs
- View habit details
- Archive and unarchive habits
- Permanently delete habits only when they have no logs
- View daily dashboard
- Track current streaks and best streaks
- Track weekly habit completion
- Safe JSON storage with validation and backups

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

## How to Run

1. Clone repo
2. Run main.py

## Project Structure

main.py  
habits.py  
stats.py  
storage.py  
validators.py  
utils.py

## Future Improvements

- SQLite database
- GUI / Web version
- Charts dashboard
- User accounts
