import main


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