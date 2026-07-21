from datetime import date, timedelta

TODAY = date.today()
YESTERDAY = TODAY - timedelta(days=1)
FUTURE = TODAY + timedelta(days=30)


def _advance_to_done(client, task_id: str) -> dict:
    r = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    assert r.status_code == 200
    r = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    assert r.status_code == 200
    return r.json()


# ============================================================
# POST /tasks - due date input
# ============================================================


def test_create_task_with_valid_due_date_returns_201_and_echoes_date(client):
    r = client.post("/tasks", json={"title": "task with due date", "due_date": FUTURE.isoformat()})
    assert r.status_code == 201
    body = r.json()
    assert body["due_date"] == FUTURE.isoformat()
    assert body["is_overdue"] is False


def test_create_task_without_due_date_returns_201_null_date_not_overdue(client):
    r = client.post("/tasks", json={"title": "task without due date"})
    assert r.status_code == 201
    body = r.json()
    assert body["due_date"] is None
    assert body["is_overdue"] is False


def test_create_task_with_empty_string_due_date_returns_201_null_date(client):
    r = client.post("/tasks", json={"title": "task with empty due date", "due_date": ""})
    assert r.status_code == 201
    body = r.json()
    assert body["due_date"] is None
    assert body["is_overdue"] is False


def test_create_task_with_past_due_date_returns_201_and_is_overdue_true(client):
    r = client.post("/tasks", json={"title": "overdue task", "due_date": YESTERDAY.isoformat()})
    assert r.status_code == 201
    body = r.json()
    assert body["due_date"] == YESTERDAY.isoformat()
    assert body["is_overdue"] is True


def test_create_task_with_invalid_date_format_returns_422(client):
    r = client.post("/tasks", json={"title": "bad date format", "due_date": "not-a-date"})
    assert r.status_code == 422


def test_create_task_with_invalid_calendar_date_returns_422(client):
    r = client.post("/tasks", json={"title": "bad calendar date", "due_date": "2026-02-30"})
    assert r.status_code == 422


def test_create_task_with_integer_due_date_returns_422(client):
    r = client.post("/tasks", json={"title": "integer due date", "due_date": 20260101})
    assert r.status_code == 422


def test_create_task_with_client_supplied_is_overdue_returns_422(client):
    r = client.post("/tasks", json={"title": "client sets overdue", "is_overdue": True})
    assert r.status_code == 422


# ============================================================
# GET /tasks and GET /tasks/{id} - derived is_overdue
# ============================================================


def test_list_tasks_includes_is_overdue_on_every_task(client):
    client.post("/tasks", json={"title": "task one", "due_date": YESTERDAY.isoformat()})
    client.post("/tasks", json={"title": "task two"})
    r = client.get("/tasks")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 2
    for task in body:
        assert isinstance(task["is_overdue"], bool)


def test_get_task_by_id_includes_due_date_and_is_overdue(client):
    created = client.post("/tasks", json={"title": "task", "due_date": YESTERDAY.isoformat()}).json()
    r = client.get(f"/tasks/{created['id']}")
    assert r.status_code == 200
    body = r.json()
    assert body["due_date"] == YESTERDAY.isoformat()
    assert body["is_overdue"] is True


def test_task_due_yesterday_and_todo_is_overdue_true(client):
    created = client.post("/tasks", json={"title": "todo overdue", "due_date": YESTERDAY.isoformat()}).json()
    assert created["status"] == "ToDo"
    r = client.get(f"/tasks/{created['id']}")
    assert r.status_code == 200
    assert r.json()["is_overdue"] is True


def test_task_due_today_is_not_overdue(client):
    created = client.post("/tasks", json={"title": "due today", "due_date": TODAY.isoformat()}).json()
    r = client.get(f"/tasks/{created['id']}")
    assert r.status_code == 200
    body = r.json()
    assert body["due_date"] == TODAY.isoformat()
    assert body["is_overdue"] is False


def test_task_due_yesterday_and_done_is_overdue_false(client):
    created = client.post("/tasks", json={"title": "done overdue", "due_date": YESTERDAY.isoformat()}).json()
    done_body = _advance_to_done(client, created["id"])
    assert done_body["status"] == "Done"
    assert done_body["is_overdue"] is False
    r = client.get(f"/tasks/{created['id']}")
    assert r.status_code == 200
    assert r.json()["is_overdue"] is False


# ============================================================
# PATCH /tasks/{id} - changing and clearing
# ============================================================


def test_patch_due_date_updates_value_returns_200(client, created_task):
    r = client.patch(f"/tasks/{created_task['id']}", json={"due_date": FUTURE.isoformat()})
    assert r.status_code == 200
    assert r.json()["due_date"] == FUTURE.isoformat()


def test_patch_due_date_to_future_flips_is_overdue_to_false(client):
    created = client.post("/tasks", json={"title": "overdue", "due_date": YESTERDAY.isoformat()}).json()
    assert created["is_overdue"] is True
    r = client.patch(f"/tasks/{created['id']}", json={"due_date": FUTURE.isoformat()})
    assert r.status_code == 200
    body = r.json()
    assert body["due_date"] == FUTURE.isoformat()
    assert body["is_overdue"] is False


def test_patch_due_date_to_null_clears_it_and_is_overdue_false(client):
    created = client.post("/tasks", json={"title": "overdue", "due_date": YESTERDAY.isoformat()}).json()
    r = client.patch(f"/tasks/{created['id']}", json={"due_date": None})
    assert r.status_code == 200
    body = r.json()
    assert body["due_date"] is None
    assert body["is_overdue"] is False


def test_patch_omitting_due_date_leaves_existing_value_unchanged(client):
    created = client.post("/tasks", json={"title": "has due date", "due_date": FUTURE.isoformat()}).json()
    r = client.patch(f"/tasks/{created['id']}", json={"title": "renamed"})
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "renamed"
    assert body["due_date"] == FUTURE.isoformat()


def test_patch_invalid_due_date_format_returns_422(client, created_task):
    r = client.patch(f"/tasks/{created_task['id']}", json={"due_date": "not-a-date"})
    assert r.status_code == 422


def test_patch_due_date_with_boolean_returns_422(client, created_task):
    r = client.patch(f"/tasks/{created_task['id']}", json={"due_date": True})
    assert r.status_code == 422


def test_patch_due_date_on_missing_task_returns_404(client):
    r = client.patch("/tasks/does-not-exist", json={"due_date": FUTURE.isoformat()})
    assert r.status_code == 404


# ============================================================
# GET /tasks?overdue= - filtering
# ============================================================


def test_filter_overdue_true_returns_only_overdue_tasks(client):
    overdue = client.post("/tasks", json={"title": "overdue", "due_date": YESTERDAY.isoformat()}).json()
    client.post("/tasks", json={"title": "future", "due_date": FUTURE.isoformat()})
    client.post("/tasks", json={"title": "no date"})

    r = client.get("/tasks", params={"overdue": "true"})
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["id"] == overdue["id"]
    assert body[0]["is_overdue"] is True


def test_filter_overdue_false_returns_only_non_overdue_tasks(client):
    client.post("/tasks", json={"title": "overdue", "due_date": YESTERDAY.isoformat()})
    future = client.post("/tasks", json={"title": "future", "due_date": FUTURE.isoformat()}).json()
    no_date = client.post("/tasks", json={"title": "no date"}).json()

    r = client.get("/tasks", params={"overdue": "false"})
    assert r.status_code == 200
    body = r.json()
    ids = {task["id"] for task in body}
    assert ids == {future["id"], no_date["id"]}
    for task in body:
        assert task["is_overdue"] is False


def test_filter_overdue_true_and_status_combines_with_and(client):
    todo_overdue = client.post("/tasks", json={"title": "todo overdue", "due_date": YESTERDAY.isoformat()}).json()
    in_progress_overdue = client.post(
        "/tasks", json={"title": "in progress overdue", "due_date": YESTERDAY.isoformat()}
    ).json()
    r = client.patch(f"/tasks/{in_progress_overdue['id']}", json={"status": "InProgress"})
    assert r.status_code == 200

    r = client.get("/tasks", params={"overdue": "true", "status": "ToDo"})
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["id"] == todo_overdue["id"]
    assert body[0]["status"] == "ToDo"
    assert body[0]["is_overdue"] is True


def test_filter_overdue_true_and_priority_combines_with_and(client):
    high_overdue = client.post(
        "/tasks", json={"title": "high overdue", "due_date": YESTERDAY.isoformat(), "priority": "High"}
    ).json()
    client.post("/tasks", json={"title": "low overdue", "due_date": YESTERDAY.isoformat(), "priority": "Low"})

    r = client.get("/tasks", params={"overdue": "true", "priority": "High"})
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["id"] == high_overdue["id"]
    assert body[0]["priority"] == "High"
    assert body[0]["is_overdue"] is True


def test_filter_overdue_true_and_status_done_returns_200_empty_list(client):
    created = client.post("/tasks", json={"title": "overdue done", "due_date": YESTERDAY.isoformat()}).json()
    _advance_to_done(client, created["id"])

    r = client.get("/tasks", params={"overdue": "true", "status": "Done"})
    assert r.status_code == 200
    assert r.json() == []


def test_filter_overdue_invalid_value_returns_422(client):
    r = client.get("/tasks", params={"overdue": "notabool"})
    assert r.status_code == 422
