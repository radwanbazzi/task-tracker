from app import storage


# ---------------------------------------------------------------------------
# POST /tasks/{task_id}/comments
# ---------------------------------------------------------------------------


def test_add_comment_returns_201_with_full_body(client, created_task):
    task_id = created_task["id"]

    response = client.post(
        f"/tasks/{task_id}/comments",
        json={"text": "This is a comment", "author": "Alice"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["task_id"] == task_id
    assert body["text"] == "This is a comment"
    assert body["author"] == "Alice"
    assert "id" in body
    assert "created_at" in body


def test_add_comment_trims_surrounding_whitespace_from_text(client, created_task):
    task_id = created_task["id"]

    response = client.post(
        f"/tasks/{task_id}/comments",
        json={"text": "  padded text  "},
    )

    assert response.status_code == 201
    assert response.json()["text"] == "padded text"


def test_add_comment_without_author_stores_null_author(client, created_task):
    task_id = created_task["id"]

    response = client.post(f"/tasks/{task_id}/comments", json={"text": "no author here"})

    assert response.status_code == 201
    assert response.json()["author"] is None


def test_add_comment_with_whitespace_only_author_stores_null_author(client, created_task):
    task_id = created_task["id"]

    response = client.post(
        f"/tasks/{task_id}/comments",
        json={"text": "some text", "author": "   "},
    )

    assert response.status_code == 201
    assert response.json()["author"] is None


def test_add_comment_blank_text_returns_422_with_exact_detail_message(client, created_task):
    task_id = created_task["id"]

    response = client.post(f"/tasks/{task_id}/comments", json={"text": ""})

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail[0]["msg"] == "Value error, Comment text is required and cannot be blank"


def test_add_comment_whitespace_only_text_returns_422(client, created_task):
    task_id = created_task["id"]

    response = client.post(f"/tasks/{task_id}/comments", json={"text": "    "})

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail[0]["msg"] == "Value error, Comment text is required and cannot be blank"


def test_add_comment_text_over_1000_chars_returns_422(client, created_task):
    task_id = created_task["id"]

    response = client.post(
        f"/tasks/{task_id}/comments",
        json={"text": "a" * 1001},
    )

    assert response.status_code == 422


def test_add_comment_author_over_50_chars_returns_422(client, created_task):
    task_id = created_task["id"]

    response = client.post(
        f"/tasks/{task_id}/comments",
        json={"text": "valid text", "author": "a" * 51},
    )

    assert response.status_code == 422


def test_add_comment_unknown_field_returns_422(client, created_task):
    task_id = created_task["id"]

    response = client.post(
        f"/tasks/{task_id}/comments",
        json={"text": "valid text", "bogus": "value"},
    )

    assert response.status_code == 422


def test_add_comment_to_missing_task_returns_404(client):
    response = client.post("/tasks/nonexistent/comments", json={"text": "valid text"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


# ---------------------------------------------------------------------------
# GET /tasks/{task_id}/comments
# ---------------------------------------------------------------------------


def test_list_comments_returns_all_comments_for_task(client, created_task):
    task_id = created_task["id"]
    client.post(f"/tasks/{task_id}/comments", json={"text": "first comment"})
    client.post(f"/tasks/{task_id}/comments", json={"text": "second comment"})

    response = client.get(f"/tasks/{task_id}/comments")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    texts = {comment["text"] for comment in body}
    assert texts == {"first comment", "second comment"}


def test_list_comments_for_task_with_none_returns_200_empty_list(client, created_task):
    task_id = created_task["id"]

    response = client.get(f"/tasks/{task_id}/comments")

    assert response.status_code == 200
    assert response.json() == []


def test_list_comments_excludes_other_tasks_comments(client, created_task):
    task_a_id = created_task["id"]
    task_b = client.post("/tasks", json={"title": "task b"})
    assert task_b.status_code == 201
    task_b_id = task_b.json()["id"]

    client.post(f"/tasks/{task_a_id}/comments", json={"text": "comment for a"})

    response = client.get(f"/tasks/{task_b_id}/comments")

    assert response.status_code == 200
    assert response.json() == []


def test_list_comments_returns_oldest_first(client, created_task):
    task_id = created_task["id"]
    client.post(f"/tasks/{task_id}/comments", json={"text": "comment one"})
    client.post(f"/tasks/{task_id}/comments", json={"text": "comment two"})
    client.post(f"/tasks/{task_id}/comments", json={"text": "comment three"})

    response = client.get(f"/tasks/{task_id}/comments")

    assert response.status_code == 200
    texts = [comment["text"] for comment in response.json()]
    assert texts == ["comment one", "comment two", "comment three"]


def test_list_comments_for_missing_task_returns_404(client):
    response = client.get("/tasks/nonexistent/comments")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


# ---------------------------------------------------------------------------
# DELETE /tasks/{task_id}/comments/{comment_id}
# ---------------------------------------------------------------------------


def test_delete_comment_returns_204_no_body(client, created_task):
    task_id = created_task["id"]
    create_response = client.post(f"/tasks/{task_id}/comments", json={"text": "to delete"})
    comment_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}/comments/{comment_id}")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_comment_removes_it_from_subsequent_list(client, created_task):
    task_id = created_task["id"]
    keep_response = client.post(f"/tasks/{task_id}/comments", json={"text": "keep me"})
    remove_response = client.post(f"/tasks/{task_id}/comments", json={"text": "remove me"})
    keep_id = keep_response.json()["id"]
    remove_id = remove_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}/comments/{remove_id}")
    assert delete_response.status_code == 204

    list_response = client.get(f"/tasks/{task_id}/comments")
    assert list_response.status_code == 200
    remaining = list_response.json()
    assert len(remaining) == 1
    assert remaining[0]["id"] == keep_id


def test_delete_missing_comment_returns_404(client, created_task):
    task_id = created_task["id"]

    response = client.delete(f"/tasks/{task_id}/comments/nonexistent")

    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"


def test_delete_comment_belonging_to_another_task_returns_404(client, created_task):
    task_a_id = created_task["id"]
    task_b = client.post("/tasks", json={"title": "task b"})
    assert task_b.status_code == 201
    task_b_id = task_b.json()["id"]

    comment_response = client.post(f"/tasks/{task_a_id}/comments", json={"text": "belongs to a"})
    comment_id = comment_response.json()["id"]

    response = client.delete(f"/tasks/{task_b_id}/comments/{comment_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"


def test_delete_comment_on_missing_task_returns_404(client):
    response = client.delete("/tasks/nonexistent/comments/nonexistent")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


# ---------------------------------------------------------------------------
# comment_count as a derived task field
# ---------------------------------------------------------------------------


def test_task_response_includes_comment_count_zero_by_default(client, created_task):
    task_id = created_task["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["comment_count"] == 0


def test_comment_count_increases_after_adding_comment(client, created_task):
    task_id = created_task["id"]
    client.post(f"/tasks/{task_id}/comments", json={"text": "a comment"})

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["comment_count"] == 1


def test_comment_count_decreases_after_deleting_comment(client, created_task):
    task_id = created_task["id"]
    first = client.post(f"/tasks/{task_id}/comments", json={"text": "first"})
    client.post(f"/tasks/{task_id}/comments", json={"text": "second"})
    first_id = first.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}/comments/{first_id}")
    assert delete_response.status_code == 204

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["comment_count"] == 1


def test_comment_count_present_on_list_tasks_endpoint(client, created_task):
    task_id = created_task["id"]
    client.post(f"/tasks/{task_id}/comments", json={"text": "a comment"})

    response = client.get("/tasks")

    assert response.status_code == 200
    tasks = response.json()
    matching = [task for task in tasks if task["id"] == task_id]
    assert len(matching) == 1
    assert matching[0]["comment_count"] == 1


def test_client_supplied_comment_count_returns_422(client):
    response = client.post("/tasks", json={"title": "sneaky task", "comment_count": 5})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Cascade delete
# ---------------------------------------------------------------------------


def test_deleting_task_removes_its_comments_from_storage(client, created_task):
    task_id = created_task["id"]
    comment_response = client.post(f"/tasks/{task_id}/comments", json={"text": "will be gone"})
    comment_id = comment_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204

    assert comment_id not in storage._comments
    assert all(c.task_id != task_id for c in storage._comments.values())


def test_deleting_task_does_not_remove_other_tasks_comments(client, created_task):
    task_a_id = created_task["id"]
    task_b = client.post("/tasks", json={"title": "task b"})
    assert task_b.status_code == 201
    task_b_id = task_b.json()["id"]

    client.post(f"/tasks/{task_a_id}/comments", json={"text": "comment for a"})
    comment_b_response = client.post(f"/tasks/{task_b_id}/comments", json={"text": "comment for b"})
    comment_b_id = comment_b_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_a_id}")
    assert delete_response.status_code == 204

    assert comment_b_id in storage._comments
    assert storage._comments[comment_b_id].task_id == task_b_id
