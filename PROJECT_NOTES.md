# Habit Tracker Project Notes

## 1. Project Purpose

This project is a command-line habit tracker built with Python.

It helps track:

* habits
* daily logs
* weekly targets
* streaks
* missed habits
* archived habits
* dashboard summaries

The long-term goal is to slowly evolve this project into a personal growth system for tracking habits, goals, learning, fitness, discipline, and progress.

The project should stay:

* clean
* simple
* modular
* tested
* practical
* easy to understand

---

## 2. Core Data Structure

The whole app is built around one main dictionary:

```python
data = {
    "habits": {},
    "logs": []
}
```

---

## 3. Habits

A habit is stored inside `data["habits"]`.

Example:

```python
"Workout": {
    "target_per_week": 5,
    "created_at": "2026-06-01",
    "archived_at": None
}
```

A habit stores:

* the habit name
* weekly target
* creation date
* archive date, if archived

Important note:

The habit name is currently used as the habit ID.

That means if a habit is renamed, all matching logs must also be updated.

---

## 4. Logs

A log is stored inside `data["logs"]`.

Example:

```python
{
    "habit": "Workout",
    "date": "2026-06-14"
}
```

A log stores:

* which habit was completed
* the date it was completed

Logs are separate from habits.

This means one habit can have many logs.

---

## 5. Simple Mental Model

The project flow is:

```txt
User input
    ↓
main.py
    ↓
validators.py
    ↓
habits.py / stats.py
    ↓
helpers.py / utils.py
    ↓
storage.py
```

In simple words:

```txt
Ask user → Validate input → Do action → Save data → Show result
```

---

## 6. File Responsibilities

## `main.py`

Controls the command-line app.

It is responsible for:

* showing the menu
* asking the user for input
* calling the correct handler function
* calling business logic functions
* saving data after changes
* showing messages to the user

Important functions:

```python
handle_add()
handle_log()
handle_view_logs()
handle_view_habit_details()
handle_delete_log()
handle_delete()
handle_toggle_archive()
handle_dashboard()
main()
```

`main.py` should coordinate actions, not contain too much business logic.

---

## `habits.py`

Contains the main habit actions.

It is responsible for changing habit and log data.

Important functions:

```python
add_habit()
log_habit()
log_multiple_habits()
delete_log()
delete_habit()
archive_habit()
unarchive_habit()
toggle_archive_habit()
```

This file answers:

> What changes are allowed to the habit data?

Examples:

* Can this habit be added?
* Can this habit be logged?
* Can this habit be deleted?
* Can this habit be archived?

---

## `stats.py`

Calculates habit progress.

It is responsible for reading data and producing useful stats.

Important functions:

```python
daily_stats()
habit_weekly_completion()
streaks()
current_streak()
best_streak()
logs_by_habit()
```

This file answers:

* What habits were completed today?
* What habits are pending?
* What is the current streak?
* What is the best streak?
* How much weekly progress has been completed?

`stats.py` should mostly calculate, not modify data.

---

## `storage.py`

Handles loading and saving data.

It is responsible for:

* creating default data
* loading data from JSON
* saving data to JSON
* validating data before saving
* creating backups
* resetting broken data when needed
* migrating old data structures

Important functions:

```python
load_data()
save_data()
create_default_data()
create_data_file()
create_backup()
backup_and_reset()
migrate_data()
```

This file protects the project from data loss.

---

## `validators.py`

Checks whether input and stored data are valid.

It is responsible for:

* validating habit names
* validating numbers
* validating dates
* validating menu choices
* validating the full JSON data structure

Important functions:

```python
validate_string()
validate_int()
validate_date()
validate_choice()
get_valid_input()
validate_data_structure()
validate_habits_data_structure()
validate_logs_data_structure()
```

This file protects the app from bad input and broken data.

---

## `helpers.py`

Contains support functions used across the app.

It is responsible for:

* displaying messages
* formatting text
* checking habit status
* preparing dashboard sections
* preparing habit detail information

Important functions:

```python
display_message()
display_numbered_list()
ensure_habits_exist()
habit_exists()
is_habit_archived()
habit_has_logs()
get_habit_details()
get_dashboard_data()
format_recovery_hint()
```

This file supports the main flow and avoids repeated code.

---

## `utils.py`

Contains shared utility functions, especially for menus.

It is responsible for:

* selecting habits
* formatting habit labels
* building archive-aware menus
* handling operation results

Important functions:

```python
get_selected_habits()
format_habit_label()
build_archive_menu_entries()
display_habit_archive_menu()
handle_operation_result()
```

---

## `config.py`

Stores project configuration values.

Examples:

```python
DATA_FILE
BACKUP_FILE
```

This keeps important constants in one place.

---

## 7. Source Files and Test Files

Each main source file has a matching test file.

```txt
habits.py      → tests/test_habits.py
stats.py       → tests/test_stats.py
storage.py     → tests/test_storage.py
validators.py → tests/test_validators.py
helpers.py     → tests/test_helpers.py
utils.py       → tests/test_utils.py
main.py        → tests/test_main.py
```

When changing a source file, check or update the matching test file.

---

## 8. Functions That Modify Data

These functions change the `data` dictionary:

```python
add_habit()
log_habit()
log_multiple_habits()
delete_log()
delete_habit()
archive_habit()
unarchive_habit()
toggle_archive_habit()
```

These functions must be tested carefully because they affect stored user data.

---

## 9. Functions That Read or Analyze Data

These functions mostly read data and return results:

```python
daily_stats()
habit_weekly_completion()
streaks()
current_streak()
best_streak()
logs_by_habit()
get_habit_details()
get_dashboard_data()
```

These functions should not unexpectedly modify `data`.

---

## 10. Important Project Rule

Habit names are currently used as keys.

Example:

```python
data["habits"]["Workout"]
```

Logs refer to habits by name:

```python
{"habit": "Workout", "date": "2026-06-14"}
```

So if a habit name changes, every matching log must also change.

Example:

```txt
Workout → Training
```

Then this must change:

```python
data["habits"]["Workout"]
```

to:

```python
data["habits"]["Training"]
```

And every log like this:

```python
{"habit": "Workout", "date": "2026-06-14"}
```

must become:

```python
{"habit": "Training", "date": "2026-06-14"}
```

If this is not done, the logs will point to a habit that no longer exists.

---

## 11. How to Study This Project

Do not read everything randomly.

Use this order:

1. Read `data.example.json`
2. Read `habits.py`
3. Read `tests/test_habits.py`
4. Read `stats.py`
5. Read `tests/test_stats.py`
6. Read one handler in `main.py`
7. Read the matching tests in `tests/test_main.py`

Study one file pair at a time.

Example:

```txt
habits.py + tests/test_habits.py
```

Do not jump between five files unless tracing one specific feature.

---

## 12. How to Understand Any Function

For each function, write this:

```txt
Function:
File:
Purpose:
Does it modify data?
Inputs:
Returns:
Errors it can raise:
Test file:
```

Example:

```txt
Function: add_habit
File: habits.py

Purpose:
Adds a new habit to data["habits"].

Does it modify data?
Yes.

Inputs:
data, habit name, target per week, created date

Returns:
Success message.

Errors it can raise:
- invalid habit name
- invalid weekly target
- habit already exists

Test file:
tests/test_habits.py
```

---

## 13. Current Project Stage

Current stage:

```txt
Intermediate CLI Habit Tracker
```

Approximate completion:

```txt
75–80%
```

The project is already:

* useful
* tested
* structured
* reliable
* good enough to show as a serious learner project

It is not advanced yet because it is still:

* CLI-only
* JSON-based
* local-only
* missing edit features
* not yet a full personal growth system

---

## 14. Main Strengths

The project already has:

* strong test coverage
* JSON validation
* backups
* habit creation
* habit logging
* habit deletion rules
* archive/unarchive support
* streak tracking
* weekly progress
* dashboard summary
* useful real-life tracking features

---

## 15. Main Risks

The main risks are:

1. Habit name is used as the ID
2. Renaming habits must update logs
3. `main.py` is becoming large
4. `helpers.py` may become too broad over time
5. New features must be kept small and tested

---

## 16. Next Feature Area

The next useful feature area is:

```txt
Edit habit
```

This includes:

* rename habit
* edit weekly target

The safest order is:

1. Add core rename function in `habits.py`
2. Add tests for rename function
3. Add core target-edit function in `habits.py`
4. Add tests for target edit
5. Add CLI handler in `main.py`
6. Add menu option
7. Add main handler tests

---

## 17. Project Development Rule

Before adding any feature:

1. Understand what data it changes
2. Add or update the core function
3. Add tests
4. Only then connect it to the CLI

Do not start with the menu.

The menu is only the surface.

The real feature should work before the user interface calls it.

---

## 18. Simple Summary

This project has three main ideas:

```txt
Habits = things I want to track
Logs = dates when I completed them
Stats = meaning created from habits and logs
```

The app flow is:

```txt
main.py gets input
validators.py checks input
habits.py changes data
stats.py calculates progress
storage.py saves data
helpers.py and utils.py support display and menus
```

If I understand `data`, `habits.py`, and `stats.py`, I understand most of the project.
