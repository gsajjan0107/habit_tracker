import copy
import main
import helpers


# ===== data helpers =====

def make_habit(target=5, created_at="2026-05-01", archived_at=None):
    return {
        "target_per_week": target,
        "created_at": created_at,
        "archived_at": archived_at,
    }


def make_log(habit="Workout", date="2026-05-01"):
    return {
        "habit": habit,
        "date": date,
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

def test_handle_add_adds_new_habit_and_saves_data(monkeypatch):
    data = make_data()

    messages, save_calls = run_handle_add(
        monkeypatch,
        data,
        user_inputs=[
            "Workout",
            "5",
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
            "WrongName",
        ],
    )

    assert "Habit name did not match. Deletion cancelled." in messages
    assert save_calls == []
    assert data == make_data(
        habits={
            "Workout": make_habit(),
        },
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
    )


def test_handle_delete_cancels_when_user_declines_confirmation(monkeypatch):
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
            "n",
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


def test_handle_delete_deletes_habit_after_full_confirmation(monkeypatch):
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

    assert len(save_calls) == 1
    assert "Workout" not in data["habits"]
    assert data["logs"] == []
    assert "Workout deleted." in messages


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
        logs=[
            make_log("Workout", "2026-05-01"),
        ],
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
    assert data["logs"] == [
        make_log("Workout", "2026-05-01"),
    ]


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
            "2026-05-01",
        ],
    )

    assert "\n==== VIEW LOGS ====" in messages
    assert "\n✅ Logged habits (2):" in messages
    assert numbered_lists == [["Reading", "Workout"]]


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
            "2026-05-02",
        ],
    )

    assert "\n==== VIEW LOGS ====" in messages
    assert "\n📅 Date: Saturday, 02 May 2026" in messages
    assert "No habits logged on Saturday, 02 May 2026." in messages
    assert numbered_lists == []


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
            "bad-date",
            "2026-05-01",
        ],
    )

    assert any("Use format YYYY-MM-DD" in message for message in messages)
    assert "\n==== VIEW LOGS ====" in messages
    assert "\n✅ Logged habits (1):" in messages
    assert numbered_lists == [["Workout"]]


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


def test_handle_dashboard_shows_completed_and_unfinished_habits(monkeypatch):
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


def test_handle_dashboard_shows_previous_day_missed_habits(monkeypatch):
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

    assert "\n⚠️ Previous Day Missed" in messages
    assert "Not logged on Friday, 01 May 2026 (2 habits):" in messages
    assert ["Reading", "Workout"] in numbered_lists


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

    messages, numbered_lists = run_handle_dashboard(
        monkeypatch,
        data,
        user_inputs=[
            "2026-05-02",
        ],
    )

    assert "\n==== DASHBOARD ====" in messages
    assert "\n⚠️ Previous Day Missed" not in messages
    assert all(
        "Not logged on Friday, 01 May 2026" not in message
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

