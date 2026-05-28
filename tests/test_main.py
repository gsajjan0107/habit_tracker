import main
import helpers


def test_handle_toggle_archive_can_be_cancelled(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [],
    }

    messages = []

    monkeypatch.setattr("builtins.input", lambda _: "q")
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_handle_operation_result(data, result):
        raise AssertionError("handle_operation_result should not be called when cancelled")

    monkeypatch.setattr(main, "handle_operation_result", fake_handle_operation_result)

    main.handle_toggle_archive(data)

    assert "Archive/unarchive cancelled." in messages
    assert data["habits"]["Workout"]["archived_at"] is None


def test_handle_delete_log_can_be_cancelled_after_selecting_date(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }

    messages = []

    inputs = iter(["2026-05-01", "q"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_save_data(data):
        raise AssertionError("save_data should not be called when deletion is cancelled")

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_delete_log(data)

    assert "Log deletion cancelled." in messages
    assert data["logs"] == [
        {
            "habit": "Workout",
            "date": "2026-05-01",
        }
    ]


def test_handle_delete_can_be_cancelled_at_habit_selection(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }

    messages = []

    monkeypatch.setattr("builtins.input", lambda _: "q")
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_save_data(data):
        raise AssertionError("save_data should not be called when deletion is cancelled")

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_delete(data)

    assert "Deletion cancelled." in messages
    assert data == {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }


def test_handle_delete_cancels_when_typed_habit_name_does_not_match(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }

    messages = []

    inputs = iter([
        "1",        # select Workout
        "y",        # confirm deletion
        "WrongName" # wrong final typed habit name
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_save_data(data):
        raise AssertionError("save_data should not be called when habit name does not match")

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_delete(data)

    assert "Habit name did not match. Deletion cancelled." in messages
    assert data == {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }


def test_handle_delete_cancels_when_user_declines_confirmation(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }

    messages = []

    inputs = iter([
        "1",  # select Workout
        "n",  # decline deletion confirmation
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_save_data(data):
        raise AssertionError("save_data should not be called when deletion is declined")

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_delete(data)

    assert "Deletion cancelled." in messages
    assert data == {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }


def test_handle_delete_deletes_habit_after_full_confirmation(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }

    messages = []
    saved = {"called": False}

    inputs = iter([
        "1",        # select Workout
        "y",        # confirm deletion
        "Workout",  # type exact habit name
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_save_data(updated_data):
        saved["called"] = True
        assert updated_data == data

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_delete(data)

    assert saved["called"] is True
    assert "Workout" not in data["habits"]
    assert data["logs"] == []
    assert "Workout deleted." in messages


def test_handle_toggle_archive_archives_selected_active_habit(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [],
    }

    called = {"handled": False}

    monkeypatch.setattr("builtins.input", lambda _: "1")

    def fake_handle_operation_result(updated_data, result):
        called["handled"] = True

        assert updated_data == data
        assert result["success"] is True
        assert "archived" in result["msg"].lower()

    monkeypatch.setattr(main, "handle_operation_result", fake_handle_operation_result)

    main.handle_toggle_archive(data)

    assert called["handled"] is True
    assert data["habits"]["Workout"]["archived_at"] is not None


def test_handle_toggle_archive_unarchives_selected_archived_habit(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": "2026-05-10",
            }
        },
        "logs": [],
    }

    called = {"handled": False}

    monkeypatch.setattr("builtins.input", lambda _: "1")

    def fake_handle_operation_result(updated_data, result):
        called["handled"] = True

        assert updated_data == data
        assert result["success"] is True
        assert "unarchived" in result["msg"].lower()

    monkeypatch.setattr(main, "handle_operation_result", fake_handle_operation_result)

    main.handle_toggle_archive(data)

    assert called["handled"] is True
    assert data["habits"]["Workout"]["archived_at"] is None


def test_handle_log_can_be_cancelled_at_habit_selection(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [],
    }

    messages = []

    inputs = iter([
        "2026-05-01",  # select date
        "q",           # cancel habit selection
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_save_data(data):
        raise AssertionError("save_data should not be called when logging is cancelled")

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_log(data)

    assert "Logging cancelled." in messages
    assert data["logs"] == []


def test_handle_log_logs_selected_habit_after_confirmation(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [],
    }

    messages = []
    saved = {"called": False}

    inputs = iter([
        "2026-05-01",  # select date
        "1",           # select Workout
        "y",           # confirm logging
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_save_data(updated_data):
        saved["called"] = True
        assert updated_data == data

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_log(data)

    assert saved["called"] is True
    assert data["logs"] == [
        {
            "habit": "Workout",
            "date": "2026-05-01",
        }
    ]
    assert any("Logged" in message for message in messages)


def test_handle_log_cancels_when_user_declines_confirmation(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [],
    }

    messages = []

    inputs = iter([
        "2026-05-01",  # select date
        "1",           # select Workout
        "n",           # decline confirmation
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_save_data(data):
        raise AssertionError("save_data should not be called when logging is declined")

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_log(data)

    assert "Logging cancelled." in messages
    assert data["logs"] == []


def test_handle_log_logs_all_pending_habits_after_confirmation(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
            "Reading": {
                "target_per_week": 3,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
        },
        "logs": [],
    }

    messages = []
    saved = {"called": False}

    inputs = iter([
        "2026-05-01",  # select date
        "all",         # select all pending habits
        "y",           # confirm logging
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_save_data(updated_data):
        saved["called"] = True
        assert updated_data == data

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_log(data)

    assert data["logs"] == [
        {
            "habit": "Reading",
            "date": "2026-05-01",
        },
        {
            "habit": "Workout",
            "date": "2026-05-01",
        },
    ]
    assert any("Logged" in message for message in messages)


def test_handle_delete_log_deletes_selected_log_after_confirmation(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
            "Reading": {
                "target_per_week": 3,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
        },
        "logs": [
            {
                "habit": "Reading",
                "date": "2026-05-01",
            },
            {
                "habit": "Workout",
                "date": "2026-05-01",
            },
        ],
    }

    messages = []
    saved = {"called": False}

    inputs = iter([
        "2026-05-01",  # select date
        "1",           # select Reading because logged habits are sorted alphabetically
        "y",           # confirm deletion
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_save_data(updated_data):
        saved["called"] = True
        assert updated_data == data

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_delete_log(data)

    assert saved["called"] is True
    assert data["logs"] == [
        {
            "habit": "Workout",
            "date": "2026-05-01",
        }
    ]
    assert any("Deleted" in message for message in messages)


def test_handle_delete_log_cancels_when_user_declines_confirmation(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }

    messages = []

    inputs = iter([
        "2026-05-01",  # select date
        "1",           # select Workout
        "n",           # decline deletion
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_save_data(data):
        raise AssertionError("save_data should not be called when delete log is declined")

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_delete_log(data)

    assert "Log deletion cancelled." in messages
    assert data["logs"] == [
        {
            "habit": "Workout",
            "date": "2026-05-01",
        }
    ]


def test_handle_delete_log_deletes_all_logs_for_date_after_confirmation(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
            "Reading": {
                "target_per_week": 3,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
            "Coding": {
                "target_per_week": 4,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
        },
        "logs": [
            {
                "habit": "Reading",
                "date": "2026-05-01",
            },
            {
                "habit": "Workout",
                "date": "2026-05-01",
            },
            {
                "habit": "Coding",
                "date": "2026-05-02",
            },
        ],
    }

    messages = []
    saved = {"called": False}

    inputs = iter([
        "2026-05-01",  # select date
        "all",         # select all logs on that date
        "y",           # confirm deletion
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_save_data(updated_data):
        saved["called"] = True
        assert updated_data == data

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_delete_log(data)

    assert saved["called"] is True
    assert data["logs"] == [
        {
            "habit": "Coding",
            "date": "2026-05-02",
        }
    ]
    assert any("Deleted" in message for message in messages)


def test_handle_add_adds_new_habit_and_saves_data(monkeypatch):
    data = {
        "habits": {},
        "logs": [],
    }

    messages = []
    saved = {"called": False}

    inputs = iter([
        "Workout",  # habit name
        "5",        # target per week
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_save_data(updated_data):
        saved["called"] = True
        assert updated_data == data

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_add(data)

    assert saved["called"] is True
    assert "Workout" in data["habits"]
    assert data["habits"]["Workout"]["target_per_week"] == 5
    assert data["habits"]["Workout"]["archived_at"] is None
    assert "Workout added." in messages


def test_handle_add_retries_when_habit_already_exists(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [],
    }

    messages = []
    saved = {"called": False}

    inputs = iter([
        "Workout",  # duplicate existing habit
        "Reading",  # new valid habit
        "3",        # target per week
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_save_data(updated_data):
        saved["called"] = True
        assert updated_data == data

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_add(data)

    assert "Habit already exists." in messages
    assert saved["called"] is True
    assert "Workout" in data["habits"]
    assert "Reading" in data["habits"]
    assert data["habits"]["Reading"]["target_per_week"] == 3
    assert data["habits"]["Reading"]["archived_at"] is None
    assert "Reading added." in messages


def test_handle_add_retries_when_habit_exists_but_is_archived(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": "2026-05-10",
            }
        },
        "logs": [],
    }

    messages = []
    saved = {"called": False}

    inputs = iter([
        "Workout",  # existing archived habit
        "Reading",  # new valid habit
        "3",        # target per week
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))

    def fake_save_data(updated_data):
        saved["called"] = True
        assert updated_data == data

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_add(data)

    assert "Habit exists but is archived. Unarchive it instead." in messages
    assert saved["called"] is True
    assert "Workout" in data["habits"]
    assert data["habits"]["Workout"]["archived_at"] == "2026-05-10"
    assert "Reading" in data["habits"]
    assert data["habits"]["Reading"]["target_per_week"] == 3
    assert data["habits"]["Reading"]["archived_at"] is None
    assert "Reading added." in messages


def test_handle_add_retries_when_target_is_invalid(monkeypatch):
    data = {
        "habits": {},
        "logs": [],
    }

    messages = []
    saved = {"called": False}

    inputs = iter([
        "Workout",  # valid habit name
        "0",        # invalid target
        "5",        # valid target
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))
    monkeypatch.setattr("validators.display_message", lambda msg: messages.append(msg))

    def fake_save_data(updated_data):
        saved["called"] = True
        assert updated_data == data

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_add(data)

    assert "Error: Input number must be >= 1" in messages
    assert saved["called"] is True
    assert "Workout" in data["habits"]
    assert data["habits"]["Workout"]["target_per_week"] == 5
    assert data["habits"]["Workout"]["archived_at"] is None
    assert "Workout added." in messages


def test_handle_add_retries_when_habit_name_is_invalid(monkeypatch):
    data = {
        "habits": {},
        "logs": [],
    }

    messages = []
    saved = {"called": False}

    inputs = iter([
        "ab",       # invalid habit name: too short
        "Workout",  # valid habit name
        "5",        # valid target per week
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))
    monkeypatch.setattr("validators.display_message", lambda msg: messages.append(msg))

    def fake_save_data(updated_data):
        saved["called"] = True
        assert updated_data == data

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_add(data)

    assert "Error: Minimum 3 characters required." in messages
    assert saved["called"] is True
    assert "Workout" in data["habits"]
    assert data["habits"]["Workout"]["target_per_week"] == 5
    assert data["habits"]["Workout"]["archived_at"] is None
    assert "Workout added." in messages


def test_handle_view_logs_shows_logged_habits_for_selected_date(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
            "Reading": {
                "target_per_week": 3,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
            "Coding": {
                "target_per_week": 4,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            },
            {
                "habit": "Reading",
                "date": "2026-05-01",
            },
            {
                "habit": "Coding",
                "date": "2026-05-02",
            },
        ],
    }

    messages = []
    numbered_lists = []

    monkeypatch.setattr("builtins.input", lambda _: "2026-05-01")
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))
    monkeypatch.setattr(main, "display_numbered_list", lambda items: numbered_lists.append(items))

    main.handle_view_logs(data)

    assert "\n==== VIEW LOGS ====" in messages
    assert "\n✅ Logged habits (2):" in messages
    assert numbered_lists == [["Reading", "Workout"]]


def test_handle_view_logs_shows_message_when_no_logs_for_selected_date(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }

    messages = []
    numbered_lists = []

    monkeypatch.setattr("builtins.input", lambda _: "2026-05-02")
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(msg))
    monkeypatch.setattr(main, "display_numbered_list", lambda items: numbered_lists.append(items))

    main.handle_view_logs(data)

    assert "\n==== VIEW LOGS ====" in messages
    assert "\n📅 Date: Saturday, 02 May 2026" in messages
    assert "No habits logged on Saturday, 02 May 2026." in messages
    assert numbered_lists == []


def test_handle_view_logs_retries_when_date_is_invalid(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }

    messages = []
    numbered_lists = []

    inputs = iter([
        "bad-date",    # invalid date
        "2026-05-01",  # valid date
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr(main, "display_numbered_list", lambda items: numbered_lists.append(items))

    main.handle_view_logs(data)

    assert any("Use format YYYY-MM-DD" in message for message in messages)
    assert "\n==== VIEW LOGS ====" in messages
    assert "\n✅ Logged habits (1):" in messages
    assert numbered_lists == [["Workout"]]


def test_handle_dashboard_shows_message_when_no_active_habits(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-02",
                "archived_at": None,
            }
        },
        "logs": [],
    }

    messages = []

    monkeypatch.setattr("builtins.input", lambda _: "2026-05-01")
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(str(msg)))

    main.handle_dashboard(data)

    assert "\n==== DASHBOARD ====" in messages
    assert "\n📅 Date: Friday, 01 May 2026" in messages
    assert "No habits were active on Friday, 01 May 2026." in messages


def test_handle_dashboard_shows_completed_and_unfinished_habits(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
            "Reading": {
                "target_per_week": 3,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }

    messages = []
    numbered_lists = []

    monkeypatch.setattr("builtins.input", lambda _: "2026-05-01")
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr(main, "display_numbered_list", lambda items: numbered_lists.append(items))
    monkeypatch.setattr(helpers, "display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr(helpers, "display_numbered_list", lambda items: numbered_lists.append(items))

    main.handle_dashboard(data)

    assert "\n==== DASHBOARD ====" in messages
    assert "\n📅 Date: Friday, 01 May 2026" in messages

    assert "\n✅ Completed (1 habit):" in messages
    assert "\n🚫 Unfinished (1 habit):" in messages

    assert ["Workout"] in numbered_lists
    assert ["Reading"] in numbered_lists

    assert "\n📌 Daily Summary" in messages
    assert "1/2 habits completed (50.00%) on Friday, 01 May 2026." in messages

    assert "\n📊 Weekly Progress (2 habits):" in messages
    assert "\n✅ Dashboard loaded." in messages


def test_handle_dashboard_retries_when_date_is_invalid(monkeypatch):
    data = {
        "habits": {
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            }
        },
        "logs": [
            {
                "habit": "Workout",
                "date": "2026-05-01",
            }
        ],
    }

    messages = []

    inputs = iter([
        "bad-date",    # invalid date
        "2026-05-01",  # valid date
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(str(msg)))

    main.handle_dashboard(data)

    assert any("Use format YYYY-MM-DD" in message for message in messages)
    assert "\n==== DASHBOARD ====" in messages
    assert "\n📅 Date: Friday, 01 May 2026" in messages
    assert "\n📌 Daily Summary" in messages
    assert "\n✅ Dashboard loaded." in messages


def test_handle_dashboard_shows_message_when_no_habits_exist(monkeypatch):
    data = {
        "habits": {},
        "logs": [],
    }

    messages = []

    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("helpers.display_message", lambda msg: messages.append(str(msg)))

    main.handle_dashboard(data)

    assert "No habits found. Add a habit first." in messages
    assert "\n==== DASHBOARD ====" not in messages