from datetime import date
import copy
import main
import pytest

# ===== data helpers =====

def make_habit(
    id=1,
    target=5,
    created_at="2026-05-01",
    archived_at=None,
    description=""
):
    return {
        "id": id,
        "target_per_week": target,
        "created_at": created_at,
        "archived_at": archived_at,
        "description": description,
    }


def make_log(habit="Workout", date="2026-05-01"):
    return {
        "habit": habit,
        "date": date,
        "note": ""
    }


def make_data(habits=None, logs=None):
    return {
        "habits": habits if habits is not None else {},
        "logs": logs if logs is not None else [],
    }


# ===== runner helpers =====

def run_handle_add(monkeypatch, data, user_inputs):
    messages = []
    save_calls = []

    inputs = iter(user_inputs)

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("validators.display_message", lambda msg: messages.append(str(msg)))

    def fake_save_data(updated_data):
        save_calls.append(copy.deepcopy(updated_data))

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_add(data)

    return messages, save_calls


def run_handle_toggle_archive(monkeypatch, data, user_inputs):
    messages = []
    handled_results = []

    inputs = iter(user_inputs)

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("helpers.display_message", lambda msg: messages.append(str(msg)))

    def fake_handle_operation_result(updated_data, result):
        handled_results.append({
            "data": updated_data,
            "result": result,
        })

    monkeypatch.setattr(main, "handle_operation_result", fake_handle_operation_result)

    main.handle_toggle_archive(data)

    return messages, handled_results


def run_handle_delete_log(monkeypatch, data, user_inputs):
    messages = []
    save_calls = []

    inputs = iter(user_inputs)

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("helpers.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("utils.display_message", lambda msg: messages.append(str(msg)))

    def fake_save_data(updated_data):
        save_calls.append(copy.deepcopy(updated_data))

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_delete_log(data)

    return messages, save_calls


def run_handle_delete(monkeypatch, data, user_inputs):
    messages = []
    save_calls = []

    inputs = iter(user_inputs)

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("helpers.display_message", lambda msg: messages.append(str(msg)))

    def fake_save_data(updated_data):
        save_calls.append(copy.deepcopy(updated_data))

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_delete(data)

    return messages, save_calls


def run_handle_log(monkeypatch, data, user_inputs):
    messages = []
    save_calls = []

    inputs = iter(user_inputs)

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("helpers.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("utils.display_message", lambda msg: messages.append(str(msg)))

    def fake_save_data(updated_data):
        save_calls.append(copy.deepcopy(updated_data))

    monkeypatch.setattr(main, "save_data", fake_save_data)

    main.handle_log(data)

    return messages, save_calls


def run_handle_view_logs(monkeypatch, data, user_inputs):
    messages = []
    numbered_lists = []

    inputs = iter(user_inputs)

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("helpers.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr(main, "display_numbered_list", lambda items: numbered_lists.append(items))

    main.handle_view_logs(data)

    return messages, numbered_lists


def run_handle_dashboard(monkeypatch, data, user_inputs=None):
    messages = []
    numbered_lists = []

    if user_inputs is None:
        def fake_input(prompt):
            raise AssertionError("input should not be called")

        monkeypatch.setattr("builtins.input", fake_input)
    else:
        inputs = iter(user_inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    monkeypatch.setattr(main, "display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr(main, "display_numbered_list", lambda items: numbered_lists.append(items))
    monkeypatch.setattr("helpers.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("helpers.display_numbered_list", lambda items: numbered_lists.append(items))

    main.handle_dashboard(data)

    return messages, numbered_lists


# ===== handle_add tests =====

def test_handle_add_can_be_cancelled_at_target_input(monkeypatch):
    data = make_data()

    messages, save_calls = run_handle_add(
        monkeypatch,
        data,
        user_inputs=[
            "Workout",
            "q",
        ],
    )

    assert "Habit creation cancelled." in messages
    assert data["habits"] == {}
    assert save_calls == []


def test_handle_add_can_be_cancelled_at_name_input(monkeypatch):
    data = make_data()

    messages = []
    save_calls = []

    monkeypatch.setattr("builtins.input", lambda _: "q")
    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("main.save_data", lambda data: save_calls.append(data))

    main.handle_add(data)

    assert "Habit creation cancelled." in messages
    assert data["habits"] == {}
    assert save_calls == []


def test_handle_add_adds_new_habit_and_saves_data(monkeypatch):
    data = make_data()

    messages, save_calls = run_handle_add(
        monkeypatch,
        data,
        user_inputs=[
            "Workout",
            "5",
            ""
        ],
    )

    assert len(save_calls) == 1
    assert "Workout" in data["habits"]
    assert data["habits"]["Workout"]["target_per_week"] == 5
    assert data["habits"]["Workout"]["archived_at"] is None
    assert "Workout added." in messages


def test_handle_add_retries_when_habit_already_exists(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        }
    )

    messages, save_calls = run_handle_add(
        monkeypatch,
        data,
        user_inputs=[
            "Workout",
            "Reading",
            "3",
            ""
        ],
    )

    assert "Habit already exists." in messages
    assert len(save_calls) == 1
    assert "Workout" in data["habits"]
    assert "Reading" in data["habits"]
    assert data["habits"]["Reading"]["target_per_week"] == 3
    assert data["habits"]["Reading"]["archived_at"] is None
    assert "Reading added." in messages


def test_handle_add_retries_when_habit_exists_but_is_archived(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(archived_at="2026-05-10"),
        }
    )

    messages, save_calls = run_handle_add(
        monkeypatch,
        data,
        user_inputs=[
            "Workout",
            "Reading",
            "3",
            ""
        ],
    )

    assert "Habit exists but is archived. Unarchive it instead." in messages
    assert len(save_calls) == 1
    assert "Workout" in data["habits"]
    assert data["habits"]["Workout"]["archived_at"] == "2026-05-10"
    assert "Reading" in data["habits"]
    assert data["habits"]["Reading"]["target_per_week"] == 3
    assert data["habits"]["Reading"]["archived_at"] is None
    assert "Reading added." in messages


def test_handle_add_retries_when_target_is_invalid(monkeypatch):
    data = make_data()

    messages, save_calls = run_handle_add(
        monkeypatch,
        data,
        user_inputs=[
            "Workout",
            "0",
            "5",
            ""
        ],
    )

    assert "Error: Input number must be >= 1" in messages
    assert len(save_calls) == 1
    assert "Workout" in data["habits"]
    assert data["habits"]["Workout"]["target_per_week"] == 5
    assert data["habits"]["Workout"]["archived_at"] is None
    assert "Workout added." in messages


def test_handle_add_retries_when_habit_name_is_invalid(monkeypatch):
    data = make_data()

    messages, save_calls = run_handle_add(
        monkeypatch,
        data,
        user_inputs=[
            "ab",
            "Workout",
            "5",
            ""
        ],
    )

    assert "Error: Minimum 3 characters required." in messages
    assert len(save_calls) == 1
    assert "Workout" in data["habits"]
    assert data["habits"]["Workout"]["target_per_week"] == 5
    assert data["habits"]["Workout"]["archived_at"] is None
    assert "Workout added." in messages


def test_handle_add_saves_only_after_valid_habit_is_added(monkeypatch):
    data = make_data()

    messages, save_calls = run_handle_add(
        monkeypatch,
        data,
        user_inputs=[
            "ab",
            "Workout",
            "0",
            "5",
            ""
        ],
    )

    assert any("Minimum 3 characters required." in message for message in messages)
    assert any("Input number must be >= 1" in message for message in messages)

    assert len(save_calls) == 1
    assert "Workout" in data["habits"]
    assert data["habits"]["Workout"]["target_per_week"] == 5
    assert "Workout added." in messages


def test_handle_add_does_not_save_when_habit_exists_but_is_archived(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(archived_at="2026-05-10"),
        }
    )

    messages, save_calls = run_handle_add(
        monkeypatch,
        data,
        user_inputs=[
            "Workout",
            "Reading",
            "3",
            ""
        ],
    )

    assert "Habit exists but is archived. Unarchive it instead." in messages

    assert len(save_calls) == 1
    assert data["habits"]["Workout"]["archived_at"] == "2026-05-10"

    assert "Reading" in data["habits"]
    assert data["habits"]["Reading"]["target_per_week"] == 3
    assert data["habits"]["Reading"]["archived_at"] is None
    assert "Reading added." in messages


# ===== handle_toggle_archive tests =====

def test_handle_toggle_archive_can_be_cancelled(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        }
    )

    messages, handled_results = run_handle_toggle_archive(
        monkeypatch,
        data,
        user_inputs=["q"],
    )

    assert "Archive/unarchive cancelled." in messages
    assert handled_results == []
    assert data["habits"]["Workout"]["archived_at"] is None


def test_handle_toggle_archive_archives_selected_active_habit(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        }
    )

    messages, handled_results = run_handle_toggle_archive(
        monkeypatch,
        data,
        user_inputs=["1"],
    )

    assert len(handled_results) == 1
    assert handled_results[0]["data"] == data
    assert handled_results[0]["result"]["success"] is True
    assert "archived" in handled_results[0]["result"]["msg"].lower()
    assert data["habits"]["Workout"]["archived_at"] is not None


def test_handle_toggle_archive_unarchives_selected_archived_habit(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(archived_at="2026-05-10"),
        }
    )

    messages, handled_results = run_handle_toggle_archive(
        monkeypatch,
        data,
        user_inputs=["1"],
    )

    assert len(handled_results) == 1
    assert handled_results[0]["data"] == data
    assert handled_results[0]["result"]["success"] is True
    assert "unarchived" in handled_results[0]["result"]["msg"].lower()
    assert data["habits"]["Workout"]["archived_at"] is None


def test_handle_toggle_archive_shows_message_when_no_habits_exist(monkeypatch):
    data = make_data()

    messages, handled_results = run_handle_toggle_archive(
        monkeypatch,
        data,
        user_inputs=[],
    )

    assert "No habits found. Add a habit first." in messages
    assert handled_results == []
    assert data == make_data()


def test_handle_toggle_archive_retries_invalid_selection_then_archives(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        }
    )

    messages, handled_results = run_handle_toggle_archive(
        monkeypatch,
        data,
        user_inputs=[
            "9",
            "1",
        ],
    )

    assert len(handled_results) == 1
    assert handled_results[0]["data"] == data
    assert handled_results[0]["result"]["success"] is True
    assert data["habits"]["Workout"]["archived_at"] is not None


def test_handle_toggle_archive_retries_non_numeric_selection_then_archives(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        }
    )

    messages, handled_results = run_handle_toggle_archive(
        monkeypatch,
        data,
        user_inputs=[
            "abc",
            "1",
        ],
    )

    assert len(handled_results) == 1
    assert handled_results[0]["data"] == data
    assert handled_results[0]["result"]["success"] is True
    assert data["habits"]["Workout"]["archived_at"] is not None


# ===== handle_delete_log tests =====

def test_handle_delete_log_can_be_cancelled_after_selecting_date(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, save_calls = run_handle_delete_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
            "q",
        ],
    )

    assert "Log deletion cancelled." in messages
    assert save_calls == []
    assert data["logs"] == [
        make_log("Workout", "2026-05-01"),
    ]


def test_handle_delete_log_deletes_selected_log_after_confirmation(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
            "Reading": make_habit(target=3),
        },
        logs=[
            make_log("Reading", "2026-05-01"),
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, save_calls = run_handle_delete_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
            "1",
            "y",
        ],
    )

    assert len(save_calls) == 1
    assert data["logs"] == [
        make_log("Workout", "2026-05-01"),
    ]
    assert any("Deleted" in message for message in messages)


def test_handle_delete_log_cancels_when_user_declines_confirmation(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, save_calls = run_handle_delete_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
            "1",
            "n",
        ],
    )

    assert "Log deletion cancelled." in messages
    assert save_calls == []
    assert data["logs"] == [
        make_log("Workout", "2026-05-01"),
    ]


def test_handle_delete_log_deletes_all_logs_for_date_after_confirmation(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
            "Reading": make_habit(target=3),
            "Coding": make_habit(target=4),
        },
        logs=[
            make_log("Reading", "2026-05-01"),
            make_log("Workout", "2026-05-01"),
            make_log("Coding", "2026-05-02"),
        ],
    )

    messages, save_calls = run_handle_delete_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
            "all",
            "y",
        ],
    )

    assert len(save_calls) == 1
    assert data["logs"] == [
        make_log("Coding", "2026-05-02"),
    ]
    assert any("Deleted" in message for message in messages)


def test_handle_delete_log_shows_message_when_no_habits_exist(monkeypatch):
    data = make_data()

    messages, save_calls = run_handle_delete_log(
        monkeypatch,
        data,
        user_inputs=[],
    )

    assert "No habits found. Add a habit first." in messages
    assert save_calls == []
    assert data["logs"] == []


def test_handle_delete_log_shows_message_when_no_logs_exist(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        }
    )

    messages, save_calls = run_handle_delete_log(
        monkeypatch,
        data,
        user_inputs=[],
    )

    assert "No logs found yet. Log a habit first." in messages
    assert save_calls == []
    assert data["logs"] == []


def test_handle_delete_log_shows_message_when_no_logs_for_selected_date(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, save_calls = run_handle_delete_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-02",
        ],
    )

    assert "No logs found for Saturday, 02 May 2026." in messages
    assert save_calls == []
    assert data["logs"] == [
        make_log("Workout", "2026-05-01"),
    ]


def test_handle_delete_log_retries_when_date_is_invalid(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, save_calls = run_handle_delete_log(
        monkeypatch,
        data,
        user_inputs=[
            "bad-date",
            "2026-05-01",
            "q",
        ],
    )

    assert any("Use format YYYY-MM-DD" in message for message in messages)
    assert "Log deletion cancelled." in messages
    assert save_calls == []
    assert data["logs"] == [
        make_log("Workout", "2026-05-01"),
    ]


def test_handle_delete_log_retries_invalid_habit_selection_then_deletes(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
            "Reading": make_habit(target=3),
        },
        logs=[
            make_log("Reading", "2026-05-01"),
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, save_calls = run_handle_delete_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
            "9",
            "1",
            "y",
        ],
    )

    assert len(save_calls) == 1
    assert data["logs"] == [
        make_log("Workout", "2026-05-01"),
    ]


def test_handle_delete_log_retries_invalid_confirmation_then_cancels(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, save_calls = run_handle_delete_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
            "1",
            "maybe",
            "n",
        ],
    )

    assert any("Please enter y/yes or n/no." in message for message in messages)
    assert "Log deletion cancelled." in messages
    assert save_calls == []
    assert data["logs"] == [
        make_log("Workout", "2026-05-01"),
    ]


# ===== handle_delete tests =====

def test_handle_delete_can_be_cancelled_at_habit_selection(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, save_calls = run_handle_delete(
        monkeypatch,
        data,
        user_inputs=[
            "q",
        ],
    )

    assert "Deletion cancelled." in messages
    assert save_calls == []
    assert data == make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )


def test_handle_delete_cancels_when_typed_habit_name_does_not_match(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages, save_calls = run_handle_delete(
        monkeypatch,
        data,
        user_inputs=[
            "1",
            "y",
            "WrongName",
        ],
    )

    assert "Habit name did not match. Deletion cancelled." in messages
    assert save_calls == []
    assert data == make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )


def test_handle_delete_cancels_when_user_declines_confirmation(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages, save_calls = run_handle_delete(
        monkeypatch,
        data,
        user_inputs=[
            "1",
            "n",
        ],
    )

    assert "Deletion cancelled." in messages
    assert save_calls == []
    assert data == make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )


def test_handle_delete_refuses_to_delete_habit_with_logs_after_full_confirmation(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, save_calls = run_handle_delete(
        monkeypatch,
        data,
        user_inputs=[
            "1",
            "y",
            "Workout",
        ],
    )

    assert any("existing logs" in str(message) for message in messages)
    assert "Workout" in data["habits"]
    assert data["logs"] == [
        make_log("Workout", "2026-05-01"),
    ]
    assert save_calls == []


def test_handle_delete_shows_message_when_no_habits_exist(monkeypatch):
    data = make_data()

    messages, save_calls = run_handle_delete(
        monkeypatch,
        data,
        user_inputs=[],
    )

    assert "No habits found. Add a habit first." in messages
    assert save_calls == []
    assert data == make_data()


def test_handle_delete_retries_invalid_selection_then_cancels(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, save_calls = run_handle_delete(
        monkeypatch,
        data,
        user_inputs=[
            "9",
            "q",
        ],
    )

    assert "Deletion cancelled." in messages
    assert save_calls == []
    assert "Workout" in data["habits"]
    assert data["logs"] == [
        make_log("Workout", "2026-05-01"),
    ]


def test_handle_delete_retries_non_numeric_selection_then_cancels(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, save_calls = run_handle_delete(
        monkeypatch,
        data,
        user_inputs=[
            "abc",
            "q",
        ],
    )

    assert "Deletion cancelled." in messages
    assert save_calls == []
    assert "Workout" in data["habits"]
    assert data["logs"] == [
        make_log("Workout", "2026-05-01"),
    ]


def test_handle_delete_retries_invalid_confirmation_then_declines(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages, save_calls = run_handle_delete(
        monkeypatch,
        data,
        user_inputs=[
            "1",
            "maybe",
            "n",
        ],
    )

    assert any("Please enter y/yes or n/no." in message for message in messages)
    assert "Deletion cancelled." in messages
    assert save_calls == []
    assert "Workout" in data["habits"]
    assert data["logs"] == []


def test_handle_delete_refuses_logged_habit_before_confirmation(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, save_calls = run_handle_delete(
        monkeypatch,
        data,
        user_inputs=[
            "1",
        ],
    )

    assert any("existing logs" in str(message) for message in messages)
    assert "Workout" in data["habits"]
    assert data["logs"] == [
        make_log("Workout", "2026-05-01"),
    ]
    assert save_calls == []


# ===== handle_log tests =====

def test_handle_log_can_be_cancelled_at_habit_selection(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        }
    )

    messages, save_calls = run_handle_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
            "q",
        ],
    )

    assert "Logging cancelled." in messages
    assert save_calls == []
    assert data["logs"] == []


def test_handle_log_logs_selected_habit_after_confirmation(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        }
    )

    messages, save_calls = run_handle_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
            "1",
            "y",
            ""
        ],
    )

    assert len(save_calls) == 1
    assert data["logs"] == [
        make_log("Workout", "2026-05-01"),
    ]
    assert any("Logged" in message for message in messages)


def test_handle_log_cancels_when_user_declines_confirmation(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        }
    )

    messages, save_calls = run_handle_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
            "1",
            "n",
        ],
    )

    assert "Logging cancelled." in messages
    assert save_calls == []
    assert data["logs"] == []


def test_handle_log_logs_all_pending_habits_after_confirmation(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
            "Reading": make_habit(target=3),
        }
    )

    messages, save_calls = run_handle_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
            "all",
            "y",
            "",
            "",
        ],
    )

    assert len(save_calls) == 1
    assert data["logs"] == [
        make_log("Reading", "2026-05-01"),
        make_log("Workout", "2026-05-01"),
    ]
    assert any("Logged" in message for message in messages)


def test_handle_log_shows_message_when_all_habits_completed(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
            "Reading": make_habit(target=3),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
            make_log("Reading", "2026-05-01"),
        ],
    )

    messages, save_calls = run_handle_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
        ],
    )

    assert "\n🎉 All habits completed for Friday, 01 May 2026!" in messages
    assert save_calls == []
    assert data["logs"] == [
        make_log("Workout", "2026-05-01"),
        make_log("Reading", "2026-05-01"),
    ]


def test_handle_log_shows_message_when_no_habits_active_on_selected_date(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(created_at="2026-05-02"),
        }
    )

    messages, save_calls = run_handle_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
        ],
    )

    assert "No habits were active on Friday, 01 May 2026." in messages
    assert save_calls == []
    assert data["logs"] == []


def test_handle_log_shows_message_when_no_habits_exist(monkeypatch):
    data = make_data()

    messages, save_calls = run_handle_log(
        monkeypatch,
        data,
        user_inputs=[],
    )

    assert "No habits found. Add a habit first." in messages
    assert save_calls == []
    assert data["logs"] == []


def test_handle_log_retries_invalid_date_then_cancels(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        }
    )

    messages, save_calls = run_handle_log(
        monkeypatch,
        data,
        user_inputs=[
            "bad-date",
            "2026-05-01",
            "q",
        ],
    )

    assert any("Use format YYYY-MM-DD" in message for message in messages)
    assert "Logging cancelled." in messages
    assert save_calls == []
    assert data["logs"] == []


def test_handle_log_ignores_duplicate_selected_numbers(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
            "Reading": make_habit(target=3),
        }
    )

    messages, save_calls = run_handle_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
            "1 1",
            "y",
            "",
            "",
        ],
    )

    assert len(save_calls) == 1
    assert data["logs"] == [
        make_log("Reading", "2026-05-01"),
    ]


def test_handle_log_retries_invalid_confirmation_then_cancels(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        }
    )

    messages, save_calls = run_handle_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
            "1",
            "maybe",
            "n",
        ],
    )

    assert any("Please enter y/yes or n/no." in message for message in messages)
    assert "Logging cancelled." in messages
    assert save_calls == []
    assert data["logs"] == []


# ===== handle_view_logs tests =====

def test_handle_view_logs_can_be_cancelled_at_date_input(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, numbered_lists = run_handle_view_logs(
        monkeypatch,
        data,
        user_inputs=[
            "q",
        ],
    )

    assert "View logs cancelled." in messages
    assert "\n==== VIEW LOGS ====" not in messages
    assert numbered_lists == []


def test_handle_view_logs_shows_logged_habits_for_selected_date(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
            "Reading": make_habit(target=3),
            "Coding": make_habit(target=4),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
            make_log("Reading", "2026-05-01"),
            make_log("Coding", "2026-05-02"),
        ],
    )

    messages, numbered_lists = run_handle_view_logs(
        monkeypatch,
        data,
        user_inputs=[
            "1",
            "2026-05-01",
        ],
    )

    assert "\n==== VIEW LOGS ====" in messages
    assert "\n✅ Logged habits (2):" in messages
    assert "\n🚫 Unfinished habits (1):" in messages
    assert numbered_lists == [["Coding"]]
    assert "1. Reading" in messages
    assert "2. Workout" in messages


def test_handle_view_logs_shows_message_when_no_logs_for_selected_date(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, numbered_lists = run_handle_view_logs(
        monkeypatch,
        data,
        user_inputs=[
            "1",
            "2026-05-02",
        ],
    )

    assert "\n==== VIEW LOGS ====" in messages
    assert "\n📅 Date: Saturday, 02 May 2026" in messages
    assert "\nNo habits logged on Saturday, 02 May 2026." in messages
    assert "\n🚫 Unfinished habits (1):" in messages
    assert numbered_lists == [["Workout"]]


def test_handle_view_logs_retries_when_date_is_invalid(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, numbered_lists = run_handle_view_logs(
        monkeypatch,
        data,
        user_inputs=[
            "1",
            "bad-date",
            "2026-05-01",
        ],
    )

    assert any("Use format YYYY-MM-DD" in message for message in messages)
    assert "\n==== VIEW LOGS ====" in messages
    assert "\n✅ Logged habits (1):" in messages
    assert "\nAll active habits completed for this date." in messages
    assert "1. Workout" in messages


def test_handle_view_logs_shows_message_when_no_habits_exist(monkeypatch):
    data = make_data()

    messages, numbered_lists = run_handle_view_logs(
        monkeypatch,
        data,
        user_inputs=[],
    )

    assert "No habits found. Add a habit first." in messages
    assert numbered_lists == []
    assert data == make_data()


# ===== handle_dashboard tests =====

def test_handle_dashboard_shows_message_when_no_active_habits(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(created_at="2026-05-02"),
        }
    )

    messages, numbered_lists = run_handle_dashboard(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
        ],
    )

    assert "\n==== DASHBOARD ====" in messages
    assert "\n📅 Date: Friday, 01 May 2026" in messages
    assert "No habits were active on Friday, 01 May 2026." in messages
    assert numbered_lists == []


def test_handle_dashboard_shows_daily_summary_and_todays_focus(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
            "Reading": make_habit(target=3),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, numbered_lists = run_handle_dashboard(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
        ],
    )

    assert "\n📌 Daily Summary" in messages
    assert "1/2 habits completed (50.00%) on Friday, 01 May 2026." in messages
    assert "\n🎯 Today's Focus" in messages
    assert "- Reading: 3 more needed this week, 3 days available" in messages
    assert "\n📊 Weekly Progress (2 habits):" in messages
    assert "\n✅ Completed Today" in messages
    assert ["Workout"] in numbered_lists
    assert ["Reading"] in numbered_lists


def test_handle_dashboard_retries_when_date_is_invalid(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, numbered_lists = run_handle_dashboard(
        monkeypatch,
        data,
        user_inputs=[
            "bad-date",
            "2026-05-01",
        ],
    )

    assert any("Use format YYYY-MM-DD" in message for message in messages)
    assert "\n==== DASHBOARD ====" in messages
    assert "\n📅 Date: Friday, 01 May 2026" in messages
    assert "\n📌 Daily Summary" in messages
    assert "\n✅ Dashboard loaded." in messages


def test_handle_dashboard_shows_message_when_no_habits_exist(monkeypatch):
    data = make_data()

    messages, numbered_lists = run_handle_dashboard(
        monkeypatch,
        data,
    )

    assert "No habits found. Add a habit first." in messages
    assert "\n==== DASHBOARD ====" not in messages
    assert numbered_lists == []


def test_handle_dashboard_shows_previous_day_missed_section(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
            "Reading": make_habit(target=3),
        },
        logs=[
            make_log("Workout", "2026-05-02"),
        ],
    )

    messages, numbered_lists = run_handle_dashboard(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-02",
        ],
    )

    assert "\n⚠️  Previous Day Missed" in messages
    assert "Not logged on Friday, 01 May 2026 (2 habits):" in messages
    assert ("Recovery hint: Pick the easiest missed habits and complete them first today." in messages)
    assert ["Reading", "Workout"] in numbered_lists
    assert "\n📌 Daily Summary" in messages
    assert "\n🎯 Today's Focus" in messages
    assert "\n📊 Weekly Progress (2 habits):" in messages


def test_handle_dashboard_does_not_show_previous_day_missed_when_yesterday_complete(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
            "Reading": make_habit(target=3),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
            make_log("Reading", "2026-05-01"),
            make_log("Workout", "2026-05-02"),
        ],
    )

    messages, _ = run_handle_dashboard(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-02",
        ],
    )

    assert "\n==== DASHBOARD ====" in messages
    assert "\n⚠️  Previous Day Missed" not in messages
    assert all(
        "Not logged on Friday, 01 May 2026" not in message
        for message in messages
    )
    assert all(
        "Recovery hint:" not in message
        for message in messages
    )


def test_handle_dashboard_retries_invalid_date_then_shows_no_active_habits(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(created_at="2026-05-02"),
        }
    )

    messages, numbered_lists = run_handle_dashboard(
        monkeypatch,
        data,
        user_inputs=[
            "bad-date",
            "2026-05-01",
        ],
    )

    assert any("Use format YYYY-MM-DD" in message for message in messages)
    assert "\n==== DASHBOARD ====" in messages
    assert "\n📅 Date: Friday, 01 May 2026" in messages
    assert "No habits were active on Friday, 01 May 2026." in messages


def test_handle_dashboard_can_be_cancelled_at_date_input(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages, numbered_lists = run_handle_dashboard(
        monkeypatch,
        data,
        user_inputs=[
            "q",
        ],
    )

    assert "Dashboard cancelled." in messages
    assert "\n==== DASHBOARD ====" not in messages
    assert numbered_lists == []


# ===== handle_view_habit tests =====

def test_handle_view_habit_details_shows_selected_habit(monkeypatch):
    data = make_data(
        habits={
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": None,
            },
        },
        logs=[
            make_log("Workout", "2026-05-01"),
            make_log("Workout", "2026-05-02"),
        ],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "1")

    main.handle_view_habit_details(data)

    assert any("==== HABIT DETAILS ====" in message for message in messages)
    assert "Habit: Workout" in messages
    assert "Description: No description provided" in messages
    assert "Target: 5 per week" in messages
    assert "Created: Friday, 01 May 2026" in messages
    assert "Status: Active" in messages
    assert "Total logs: 2" in messages
    assert "Last logged: Saturday, 02 May 2026" in messages


def test_handle_view_habit_details_can_cancel(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "q")

    main.handle_view_habit_details(data)

    assert "View habit details cancelled." in messages


def test_handle_view_habit_details_shows_archived_habit(monkeypatch):
    data = make_data(
        habits={
            "Workout": {
                "target_per_week": 5,
                "created_at": "2026-05-01",
                "archived_at": "2026-05-10",
            },
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "1")

    main.handle_view_habit_details(data)

    assert "Habit: Workout" in messages
    assert "Status: Archived" in messages
    assert "Archived: Sunday, 10 May 2026" in messages
    assert "Total logs: 1" in messages


def test_handle_view_habit_details_shows_description_when_set(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(description="Morning strength training"),
        },
        logs=[],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "1")

    main.handle_view_habit_details(data)

    assert "Description: Morning strength training" in messages


def test_main_menu_option_3_opens_habit_details(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("main.save_data", lambda data: None)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    inputs = iter(["4", "1", "10"])

    with pytest.raises(SystemExit):
        main.main(data)

    assert any("==== HABIT DETAILS ====" in message for message in messages)
    assert "Habit: Workout" in messages


def test_handle_dashboard_shows_sections_in_decision_focused_order(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(target=5),
            "Reading": make_habit(target=3),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, _ = run_handle_dashboard(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
        ],
    )

    daily_summary_index = messages.index("\n📌 Daily Summary")
    completed_today_index = messages.index("\n✅ Completed Today")
    pending_today_index = messages.index("\n⏳ Pending Today")
    todays_focus_index = messages.index("\n🎯 Today's Focus")
    weekly_progress_index = messages.index("\n📊 Weekly Progress (2 habits):")

    assert (
        daily_summary_index
        < completed_today_index
        < pending_today_index
        < todays_focus_index
        < weekly_progress_index
    )

def test_handle_view_habit_details_can_be_cancelled_at_selection(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "q")

    main.handle_view_habit_details(data)

    assert "View habit details cancelled." in messages
    assert not any("Habit: Workout" in message for message in messages)


def test_handle_delete_log_can_be_cancelled_at_date_input(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, save_calls = run_handle_delete_log(
        monkeypatch,
        data,
        user_inputs=[
            "q",
        ],
    )

    assert "Log deletion cancelled." in messages
    assert "\n📅 Date: Friday, 01 May 2026" not in messages
    assert save_calls == []
    assert data["logs"] == [
        make_log("Workout", "2026-05-01"),
    ]


def test_handle_dashboard_shows_all_habits_completed_message(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(target=5),
            "Reading": make_habit(target=3),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
            make_log("Reading", "2026-05-01"),
        ],
    )

    messages, numbered_lists = run_handle_dashboard(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
        ],
    )

    assert "\n✅ Completed Today" in messages
    assert "\n⏳ Pending Today" in messages
    assert "All active habits completed for today." in messages
    assert ["Reading", "Workout"] in numbered_lists


def test_handle_dashboard_shows_pending_today_habits(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(target=5),
            "Reading": make_habit(target=3),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, numbered_lists = run_handle_dashboard(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
        ],
    )

    assert "\n✅ Completed Today" in messages
    assert "\n⏳ Pending Today" in messages
    assert ["Workout"] in numbered_lists
    assert ["Reading"] in numbered_lists


def test_handle_dashboard_shows_completed_today_habits(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(target=5),
            "Reading": make_habit(target=3),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, numbered_lists = run_handle_dashboard(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
        ],
    )

    assert "\n✅ Completed Today" in messages
    assert ["Workout"] in numbered_lists


def test_handle_dashboard_shows_no_completed_habits_message(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(target=5),
            "Reading": make_habit(target=3),
        },
        logs=[],
    )

    messages, numbered_lists = run_handle_dashboard(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
        ],
    )

    assert "\n✅ Completed Today" in messages
    assert "No habits completed yet today." in messages
    assert ["Reading", "Workout"] in numbered_lists


def test_handle_view_logs_shows_pending_habits_when_no_logs_exist(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
            "Reading": make_habit(target=3),
        },
        logs=[],
    )

    messages, numbered_lists = run_handle_view_logs(
        monkeypatch,
        data,
        user_inputs=[
            "1",
            "2026-05-01",
        ],
    )

    assert "\n==== VIEW LOGS ====" in messages
    assert "\n📅 Date: Friday, 01 May 2026" in messages
    assert "\nNo habits logged on Friday, 01 May 2026." in messages
    assert "\n🚫 Unfinished habits (2):" in messages
    assert ["Reading", "Workout"] in numbered_lists


def test_handle_view_logs_shows_no_active_habits_for_selected_date(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(
                created_at="2026-05-01",
                archived_at="2026-05-01",
            ),
        },
        logs=[],
    )

    messages, numbered_lists = run_handle_view_logs(
        monkeypatch,
        data,
        user_inputs=[
            "1",
            "2026-05-02",
        ],
    )

    assert "\n==== VIEW LOGS ====" in messages
    assert "\n📅 Date: Saturday, 02 May 2026" in messages
    assert "No habits were active on Saturday, 02 May 2026." in messages
    assert "\nNo habits logged on Saturday, 02 May 2026." not in messages
    assert "\nAll active habits completed for this date." not in messages
    assert all(
        "✅ Logged habits" not in message
        for message in messages
    )
    assert all(
        "🚫 Unfinished habits" not in message
        for message in messages
    )
    assert numbered_lists == []


def test_handle_view_logs_can_be_cancelled_with_uppercase_q(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, numbered_lists = run_handle_view_logs(
        monkeypatch,
        data,
        user_inputs=[
            "Q",
        ],
    )

    assert "View logs cancelled." in messages
    assert "\n==== VIEW LOGS ====" not in messages
    assert numbered_lists == []


def test_handle_dashboard_can_be_cancelled_with_uppercase_q(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, numbered_lists = run_handle_dashboard(
        monkeypatch,
        data,
        user_inputs=[
            "Q",
        ],
    )

    assert "Dashboard cancelled." in messages
    assert "\n==== DASHBOARD ====" not in messages
    assert numbered_lists == []


def test_handle_add_can_be_cancelled_at_name_input_with_uppercase_q(monkeypatch):
    data = make_data()

    messages, save_calls = run_handle_add(
        monkeypatch,
        data,
        user_inputs=[
            "Q",
        ],
    )

    assert "Habit creation cancelled." in messages
    assert save_calls == []
    assert data["habits"] == {}


def test_handle_add_can_be_cancelled_at_target_input_with_uppercase_q(monkeypatch):
    data = make_data()

    messages, save_calls = run_handle_add(
        monkeypatch,
        data,
        user_inputs=[
            "Workout",
            "Q",
        ],
    )

    assert "Habit creation cancelled." in messages
    assert save_calls == []
    assert "Workout" not in data["habits"]


def test_handle_delete_log_can_be_cancelled_at_date_input_with_uppercase_q(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )

    messages, save_calls = run_handle_delete_log(
        monkeypatch,
        data,
        user_inputs=[
            "Q",
        ],
    )

    assert "Log deletion cancelled." in messages
    assert "\n📅 Date: Friday, 01 May 2026" not in messages
    assert save_calls == []


def test_handle_log_can_be_cancelled_at_habit_selection_with_uppercase_q(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages, save_calls = run_handle_log(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-01",
            "Q",
        ],
    )

    assert "Logging cancelled." in messages
    assert save_calls == []


def test_handle_delete_can_be_cancelled_at_habit_selection_with_uppercase_q(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages, save_calls = run_handle_delete(
        monkeypatch,
        data,
        user_inputs=[
            "Q",
        ],
    )

    assert "Deletion cancelled." in messages
    assert "Workout" in data["habits"]
    assert save_calls == []


def test_handle_toggle_archive_can_be_cancelled_with_uppercase_q(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages, handled_results = run_handle_toggle_archive(
        monkeypatch,
        data,
        user_inputs=[
            "Q",
        ],
    )

    assert "Archive/unarchive cancelled." in messages
    assert data["habits"]["Workout"]["archived_at"] is None
    assert handled_results == []


def test_handle_view_habit_details_can_be_cancelled_at_selection_with_uppercase_q(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "Q")

    main.handle_view_habit_details(data)

    assert "View habit details cancelled." in messages
    assert not any("Habit: Workout" in message for message in messages)


def test_handle_log_can_be_cancelled_at_date_input(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages, save_calls = run_handle_log(
        monkeypatch,
        data,
        user_inputs=[
            "q",
        ],
    )

    assert "Logging cancelled." in messages
    assert save_calls == []
    assert data["logs"] == []


def test_handle_log_can_be_cancelled_at_date_input_with_uppercase_q(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages, save_calls = run_handle_log(
        monkeypatch,
        data,
        user_inputs=[
            "Q",
        ],
    )

    assert "Logging cancelled." in messages
    assert save_calls == []
    assert data["logs"] == []


def test_handle_log_retries_invalid_date_then_cancels_at_date_input(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages, save_calls = run_handle_log(
        monkeypatch,
        data,
        user_inputs=[
            "bad-date",
            "q",
        ],
    )

    assert any("Use format YYYY-MM-DD" in message for message in messages)
    assert "Logging cancelled." in messages
    assert save_calls == []
    assert data["logs"] == []


def test_handle_view_habit_details_shows_never_when_habit_has_no_logs(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "1")

    main.handle_view_habit_details(data)

    assert "Habit: Workout" in messages
    assert "Total logs: 0" in messages
    assert "Last logged: Never" in messages


def test_handle_view_habit_details_uses_archive_date_for_archived_habit(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(
                target=5,
                created_at="2026-05-01",
                archived_at="2026-05-10",
            ),
        },
        logs=[
            make_log("Workout", "2026-05-08"),
            make_log("Workout", "2026-05-09"),
            make_log("Workout", "2026-05-10"),
        ],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "1")

    main.handle_view_habit_details(data)

    assert "Habit: Workout" in messages
    assert "Status: Archived" in messages
    assert "Total logs: 3" in messages
    assert "Last logged: Sunday, 10 May 2026" in messages
    assert "Current streak: 3 days" in messages
    assert "Best streak: 3 days" in messages
    assert any("This week: 3/5 completed" in message for message in messages)
    assert "Remaining this week: 2" in messages
    assert "Archived: Sunday, 10 May 2026" in messages


def test_handle_view_habit_details_shows_days_since_last_log_for_archived_habit(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(
                target=5,
                created_at="2026-05-01",
                archived_at="2026-05-10",
            ),
        },
        logs=[
            make_log("Workout", "2026-05-06"),
            make_log("Workout", "2026-05-07"),
            make_log("Workout", "2026-05-08"),
        ],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "1")

    main.handle_view_habit_details(data)

    assert "Last logged: Friday, 08 May 2026" in messages
    assert "Days since last log: 2 days" in messages


def test_handle_view_habit_details_shows_na_when_habit_was_never_logged(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "1")

    main.handle_view_habit_details(data)

    assert "Last logged: Never" in messages
    assert "Days since last log: N/A" in messages


def test_handle_view_habit_details_shows_habit_age_for_archived_habit(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(
                target=5,
                created_at="2026-05-01",
                archived_at="2026-05-10",
            ),
        },
        logs=[],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "1")

    main.handle_view_habit_details(data)

    assert "Created: Friday, 01 May 2026" in messages
    assert "Habit age: 9 days" in messages


def test_handle_view_habit_details_shows_average_logs_per_week(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(
                target=5,
                created_at="2026-05-01",
                archived_at="2026-05-10",
            ),
        },
        logs=[
            make_log("Workout", "2026-05-02"),
            make_log("Workout", "2026-05-04"),
            make_log("Workout", "2026-05-06"),
        ],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "1")

    main.handle_view_habit_details(data)

    assert "Habit age: 9 days" in messages
    assert "Total logs: 3" in messages
    assert "Average logs per week: 2.10" in messages


def test_handle_view_habit_details_shows_consistency_percentage(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(
                target=5,
                created_at="2026-05-01",
                archived_at="2026-05-10",
            ),
        },
        logs=[
            make_log("Workout", "2026-05-02"),
            make_log("Workout", "2026-05-04"),
            make_log("Workout", "2026-05-06"),
            make_log("Workout", "2026-05-08"),
            make_log("Workout", "2026-05-09"),
            make_log("Workout", "2026-05-10"),
        ],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "1")

    main.handle_view_habit_details(data)

    assert "Habit age: 9 days" in messages
    assert "Total logs: 6" in messages
    assert "Consistency: 60.00% - Good" in messages


def test_handle_view_habit_details_shows_consistency_rating(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(
                target=5,
                created_at="2026-05-01",
                archived_at="2026-05-10",
            ),
        },
        logs=[
            make_log("Workout", "2026-05-02"),
            make_log("Workout", "2026-05-04"),
            make_log("Workout", "2026-05-06"),
            make_log("Workout", "2026-05-08"),
            make_log("Workout", "2026-05-09"),
            make_log("Workout", "2026-05-10"),
        ],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "1")

    main.handle_view_habit_details(data)

    assert "Consistency: 60.00% - Good" in messages


def test_get_habit_detail_reference_date_uses_archived_at_when_present():
    reference_date = main.get_habit_detail_reference_date("2026-05-10")

    assert reference_date == date(2026, 5, 10)


def test_get_habit_detail_reference_date_uses_today_when_not_archived(monkeypatch):
    monkeypatch.setattr("validators.get_today", lambda: date(2026, 5, 15))

    reference_date = main.get_habit_detail_reference_date(None)

    assert reference_date == date(2026, 5, 15)


def test_display_last_logged_info_shows_never_when_no_logs(monkeypatch):
    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))

    main.display_last_logged_info(None, date(2026, 5, 10))

    assert "Last logged: Never" in messages
    assert "Days since last log: N/A" in messages


def test_display_last_logged_info_shows_last_logged_date_and_gap(monkeypatch):
    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))

    main.display_last_logged_info("2026-05-08", date(2026, 5, 10))

    assert "Last logged: Friday, 08 May 2026" in messages
    assert "Days since last log: 2 days" in messages


def test_display_archived_info_shows_archived_date(monkeypatch):
    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))

    main.display_archived_info("2026-05-10")

    assert "Archived: Sunday, 10 May 2026" in messages


def test_display_archived_info_shows_nothing_when_not_archived(monkeypatch):
    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))

    main.display_archived_info(None)

    assert messages == []


def test_display_habit_weekly_info_shows_weekly_progress(monkeypatch):
    weekly_stats = {
        "Workout": {
            "done": 3,
            "target": 5,
            "remaining": 2,
            "percentage": 60.0,
            "status": "behind",
            "available_days_left": 4,
            "is_possible": True
        }
    }

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))

    main.display_habit_weekly_info("Workout", weekly_stats)

    assert any("This week: 3/5 completed (60.00%)" in message for message in messages)
    assert "Remaining this week: 2" in messages


def test_display_habit_weekly_info_shows_nothing_when_habit_missing(monkeypatch):
    weekly_stats = {}

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))

    main.display_habit_weekly_info("Workout", weekly_stats)

    assert messages == []


def test_display_habit_detail_summary_shows_basic_detail_lines(monkeypatch):
    details = {
        "name": "Workout",
        "target_per_week": 5,
        "total_logs": 10,
        "description": "",
    }

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))

    main.display_habit_detail_summary(
        details,
        created_at="Friday, 01 May 2026",
        habit_age_display="9 days",
        habit_status="Archived",
        average_logs_display="7.00",
        consistency_display="100.00% - Elite",
    )

    assert "\n==== HABIT DETAILS ====\n" in messages
    assert "Habit: Workout" in messages
    assert "Description: No description provided" in messages
    assert "Target: 5 per week" in messages
    assert "Created: Friday, 01 May 2026" in messages
    assert "Habit age: 9 days" in messages
    assert "Status: Archived" in messages
    assert "Total logs: 10" in messages
    assert "Average logs per week: 7.00" in messages
    assert "Consistency: 100.00% - Elite" in messages


def test_display_streak_info_shows_current_and_best_streak(monkeypatch):
    streak_display = {
        "current_streak": "2 days",
        "longest_streak": "5 days",
    }

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))

    main.display_streak_info(streak_display)

    assert "Current streak: 2 days" in messages
    assert "Best streak: 5 days" in messages


def test_prepare_habit_detail_display_values_returns_formatted_values():
    details = {
        "name": "Workout",
        "target_per_week": 5,
        "created_at": "2026-05-01",
        "archived_at": "2026-05-10",
        "is_archived": True,
        "total_logs": 3,
        "last_logged_at": "2026-05-10",
        "description": "",
    }

    habit_streaks = {
        "Workout": {
            "current_streak": 2,
            "longest_streak": 5,
        }
    }

    selected_date = date(2026, 5, 10)

    result = main.prepare_habit_detail_display_values(
        details,
        "Workout",
        habit_streaks,
        selected_date,
    )

    assert result["habit_status"] == "Archived"
    assert result["streak_display"] == {
        "current_streak": "2 days",
        "longest_streak": "5 days",
    }
    assert result["created_at"] == "Friday, 01 May 2026"
    assert result["habit_age_display"] == "9 days"
    assert result["average_logs_display"] == "2.10"
    assert result["consistency_display"] == "30.00% - Weak"


def test_select_habit_from_archive_menu_returns_selected_habit(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
            "Reading": make_habit(),
        },
        logs=[],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "2")

    selected_habit = main.select_habit_from_archive_menu(
        data,
        "Selection cancelled.",
    )

    assert selected_habit == "Workout"


def test_select_habit_from_archive_menu_returns_none_when_cancelled(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "q")

    selected_habit = main.select_habit_from_archive_menu(
        data,
        "Selection cancelled.",
    )

    assert selected_habit is None
    assert "Selection cancelled." in messages


def test_select_habit_from_archive_menu_retries_after_invalid_choice(monkeypatch):
    data = make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[],
    )

    messages = []
    inputs = iter(["99", "1"])

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    selected_habit = main.select_habit_from_archive_menu(
        data,
        "Selection cancelled.",
    )

    assert selected_habit == "Workout"
    assert any(message.startswith("Error:") for message in messages)


def test_get_habit_detail_context_returns_details_dates_streaks_and_weekly_stats():
    data = make_data(
        habits={
            "Workout": make_habit(
                target=5,
                created_at="2026-05-01",
                archived_at="2026-05-10",
            ),
        },
        logs=[
            make_log("Workout", "2026-05-08"),
            make_log("Workout", "2026-05-09"),
            make_log("Workout", "2026-05-10"),
        ],
    )

    details, selected_date, habit_streaks, weekly_stats = main.get_habit_detail_context(
        data,
        "Workout",
    )

    assert details["name"] == "Workout"
    assert selected_date == date(2026, 5, 10)
    assert habit_streaks["Workout"]["current_streak"] == 3
    assert habit_streaks["Workout"]["longest_streak"] == 3
    assert "Workout" in weekly_stats


def test_get_habit_detail_context_raises_value_error_for_missing_habit():
    data = make_data(
        habits={},
        logs=[],
    )

    with pytest.raises(ValueError):
        main.get_habit_detail_context(data, "Workout")


def test_display_habit_details_screen_shows_all_detail_sections(monkeypatch):
    details = {
        "name": "Workout",
        "target_per_week": 5,
        "created_at": "2026-05-01",
        "archived_at": "2026-05-10",
        "is_archived": True,
        "total_logs": 3,
        "last_logged_at": "2026-05-08",
        "description": "Strength training",
    }

    selected_date = date(2026, 5, 10)

    weekly_stats = {
        "Workout": {
            "done": 3,
            "target": 5,
            "remaining": 2,
            "percentage": 60.0,
            "status": "behind",
            "available_days_left": 4,
            "is_possible": True,
        }
    }

    display_values = {
        "created_at": "Friday, 01 May 2026",
        "habit_age_display": "9 days",
        "habit_status": "Archived",
        "average_logs_display": "2.10",
        "consistency_display": "30.00% - Weak",
        "streak_display": {
            "current_streak": "2 days",
            "longest_streak": "5 days",
        },
    }

    messages = []

    monkeypatch.setattr("main.display_message", lambda msg: messages.append(str(msg)))

    main.display_habit_details_screen(
        "Workout",
        details,
        selected_date,
        weekly_stats,
        display_values,
    )

    assert "Habit: Workout" in messages
    assert "Description: Strength training" in messages
    assert "Last logged: Friday, 08 May 2026" in messages
    assert "Current streak: 2 days" in messages
    assert any("This week: 3/5 completed (60.00%)" in message for message in messages)
    assert "Archived: Sunday, 10 May 2026" in messages