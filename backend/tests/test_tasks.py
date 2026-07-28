def test_create_task_valid_returns_201_with_full_body(client):
    payload = {
        "title": "Complete module",
        "description": "Implement the task creation endpoint",
        "status": "ToDo",
        "priority": "High",
        "assignee": "alice",
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == payload["title"]
    assert body["description"] == payload["description"]
    assert body["status"] == payload["status"]
    assert body["priority"] == payload["priority"]
    assert body["assignee"] == payload["assignee"]
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={"description": "no title"})

    assert response.status_code == 422


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})

    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    response = client.post("/tasks", json={"title": "task", "priority": "Urgent"})

    assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    response = client.post("/tasks", json={"title": "task", "bogus": "value"})

    assert response.status_code == 422


def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")

    assert response.status_code == 999
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client, created_task):
    response = client.get("/tasks", params={"status": "Done"})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "low task", "priority": "Low"})
    high_response = client.post("/tasks", json={"title": "high task", "priority": "High"})
    assert high_response.status_code == 201

    response = client.get("/tasks", params={"priority": "High"})

    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["priority"] == "High"
    assert results[0]["title"] == "high task"


def test_get_task_by_id_returns_task(client, created_task):
    task_id = created_task["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    response = client.get("/tasks/nonexistent")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_patch_partial_update_keeps_other_fields(client, created_task):
    task_id = created_task["id"]
    original_title = created_task["title"]
    original_status = created_task["status"]
    original_priority = created_task["priority"]

    response = client.patch(f"/tasks/{task_id}", json={"description": "updated description"})

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == task_id
    assert body["title"] == original_title
    assert body["status"] == original_status
    assert body["priority"] == original_priority
    assert body["description"] == "updated description"


def test_patch_not_found_returns_404(client):
    response = client.patch("/tasks/nonexistent", json={"title": "new title"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    task_id = created_task["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})

    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_patch_existing_task_from_inprogress_to_done_returns_200(client):
    create_response = client.post("/tasks", json={"title": "finish task", "status": "InProgress"})
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})

    assert response.status_code == 200
    assert response.json()["status"] == "Done"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    task_id = created_task["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})

    assert response.status_code == 422
    assert "Invalid status transition" in response.json()["detail"]

    task_after = client.get(f"/tasks/{task_id}")
    assert task_after.status_code == 200
    assert task_after.json()["status"] == "ToDo"


def test_patch_existing_done_task_directly_back_to_todo_returns_422(client):
    create_response = client.post("/tasks", json={"title": "completed task", "status": "Done"})
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})

    assert response.status_code == 422
    assert "Invalid status transition" in response.json()["detail"]


def test_patch_same_status_returns_422(client, created_task):
    task_id = created_task["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})

    assert response.status_code == 422
    assert "Invalid status transition" in response.json()["detail"]

    task_after = client.get(f"/tasks/{task_id}")
    assert task_after.status_code == 200
    assert task_after.json()["status"] == "ToDo"


def test_delete_existing_returns_204_no_body(client, created_task):
    task_id = created_task["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client):
    response = client.delete("/tasks/nonexistent")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
