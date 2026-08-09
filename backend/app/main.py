from datetime import date, datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app import storage
from app.business_rules import validate_status_transition
from app.models import (
    CommentCreate,
    CommentResponse,
    TaskCreate,
    TaskPriority,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)
from app.task_rules import build_task_response

app = FastAPI(
    title="Task Tracker API",
    description="Minimal REST API skeleton for the Module 1 Task Tracker learning project.",
    version="0.1.0",
)

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # fine for local dev; tighten later
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health", status_code=200)
def health_check() -> dict[str, str]:
    """Return a simple liveness check for the API.

    Route:
        GET /health

    Returns:
        dict[str, str]: A payload with a static ``"status": "ok"`` and the
        current UTC timestamp in ISO 8601 format under ``"timestamp"``.

    Example:
        GET /health -> 200
        {"status": "ok", "timestamp": "2026-08-09T12:00:00+00:00"}
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/version", status_code=200)
def get_version() -> dict[str, str]:
    """Return the running API version.

    Route:
        GET /version

    Returns:
        dict[str, str]: A single-key payload ``{"version": <app.version>}``.

    Example:
        GET /version -> 200
        {"version": "0.1.0"}
    """
    return {"version": app.version}


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = None,
) -> list[TaskResponse]:
    """List tasks, optionally filtered by status, priority, and overdue state.

    Computes ``is_overdue`` and ``comment_count`` for every task (via
    ``build_task_response``) before returning it, then applies the
    ``overdue`` filter, if given, against the computed ``is_overdue`` value.

    Route:
        GET /tasks

    Args:
        status: Optional task status to filter by (query parameter).
            [VERIFY] An invalid enum value is rejected by FastAPI's own
            query-parameter validation (422) before this function runs,
            not by code in this function.
        priority: Optional task priority to filter by (query parameter).
            Same [VERIFY] note as ``status`` applies.
        overdue: Optional flag; when provided, only tasks whose computed
            ``is_overdue`` matches this value are returned.

    Returns:
        list[TaskResponse]: The filtered tasks, each with ``is_overdue``
        and ``comment_count`` populated.

    Example:
        GET /tasks?status=ToDo&overdue=true -> 200
        [{"id": "...", "title": "...", "status": "ToDo", "is_overdue": true, ...}]
    """
    today = date.today()
    tasks = storage.get_all_tasks(status=status, priority=priority)
    task_responses = [
        build_task_response(
            task, today=today, comment_count=storage.count_comments_for_task(task.id)
        )
        for task in tasks
    ]
    if overdue is not None:
        task_responses = [task for task in task_responses if task.is_overdue is overdue]
    return task_responses


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task.

    Route:
        POST /tasks

    Args:
        payload: Task fields to create; validated by ``TaskCreate``
            (``extra="forbid"``, so unknown fields are rejected with 422).

    Returns:
        TaskResponse: The newly created task, with ``is_overdue`` computed
        against today's date and ``comment_count`` set to 0.

    Example:
        POST /tasks {"title": "Write docs"} -> 201
        {"id": "...", "title": "Write docs", "status": "ToDo", ...}
    """
    today = date.today()
    task = storage.add_task(payload)
    return build_task_response(
        task, today=today, comment_count=storage.count_comments_for_task(task.id)
    )


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Retrieve a single task by id.

    Route:
        GET /tasks/{task_id}

    Args:
        task_id: The id of the task to fetch.

    Returns:
        TaskResponse: The task, with ``is_overdue`` and ``comment_count``
        computed.

    Raises:
        HTTPException: 404 with detail "Task not found" if no task with
            ``task_id`` exists.
    """
    today = date.today()
    task = storage.get_task_by_id(task_id)
    if task is not None:
        return build_task_response(
            task, today=today, comment_count=storage.count_comments_for_task(task_id)
        )
    raise HTTPException(status_code=404, detail="Task not found")


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Partially update a task.

    Only fields explicitly set on ``payload`` are applied; fields left
    unset are left unchanged (``exclude_unset`` semantics, applied in
    ``storage.update_task``). A ``status`` change is validated against the
    allowed transitions before being applied.

    Route:
        PATCH /tasks/{task_id}

    Args:
        task_id: The id of the task to update.
        payload: Fields to change; validated by ``TaskUpdate``
            (``extra="forbid"``, so unknown fields are rejected with 422).

    Returns:
        TaskResponse: The updated task, with ``is_overdue`` and
        ``comment_count`` recomputed.

    Raises:
        HTTPException: 404 with detail "Task not found" if no task with
            ``task_id`` exists (checked both before and, defensively,
            after calling ``storage.update_task``).
        HTTPException: 422 if ``payload.status`` is set and the transition
            from the task's current status is not one of the allowed
            transitions (see ``business_rules.VALID_TRANSITIONS``).
    """
    existing_task = storage.get_task_by_id(task_id)
    if existing_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if payload.status is not None:
        validate_status_transition(existing_task.status, payload.status)

    updated_task = storage.update_task(task_id, payload)
    if updated_task is not None:
        today = date.today()
        return build_task_response(
            updated_task,
            today=today,
            comment_count=storage.count_comments_for_task(task_id),
        )
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    """Delete a task and cascade-delete its comments.

    Route:
        DELETE /tasks/{task_id}

    Args:
        task_id: The id of the task to delete.

    Returns:
        None: Responds with 204 No Content on success.

    Raises:
        HTTPException: 404 with detail "Task not found" if no task with
            ``task_id`` exists.
    """
    if storage.delete_task(task_id):
        return None
    raise HTTPException(status_code=404, detail="Task not found")


@app.post(
    "/tasks/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["comments"],
)
def create_comment(task_id: str, payload: CommentCreate) -> CommentResponse:
    """Add a comment to a task.

    Route:
        POST /tasks/{task_id}/comments

    Args:
        task_id: The id of the task to comment on.
        payload: Comment fields; validated by ``CommentCreate``
            (``extra="forbid"``, so unknown fields are rejected with 422).

    Returns:
        CommentResponse: The newly created comment.

    Raises:
        HTTPException: 404 with detail "Task not found" if no task with
            ``task_id`` exists.
    """
    if storage.get_task_by_id(task_id) is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return storage.add_comment(task_id, payload)


@app.get(
    "/tasks/{task_id}/comments",
    response_model=list[CommentResponse],
    tags=["comments"],
)
def list_comments(task_id: str) -> list[CommentResponse]:
    """List all comments for a task, oldest first.

    Route:
        GET /tasks/{task_id}/comments

    Args:
        task_id: The id of the task whose comments to list.

    Returns:
        list[CommentResponse]: Comments in insertion order (not re-sorted
        by ``created_at``; see ``storage.get_comments_for_task``).

    Raises:
        HTTPException: 404 with detail "Task not found" if no task with
            ``task_id`` exists.
    """
    if storage.get_task_by_id(task_id) is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return storage.get_comments_for_task(task_id)


@app.delete(
    "/tasks/{task_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["comments"],
)
def delete_comment(task_id: str, comment_id: str) -> None:
    """Delete a single comment from a task.

    Route:
        DELETE /tasks/{task_id}/comments/{comment_id}

    Args:
        task_id: The id of the task the comment is expected to belong to.
        comment_id: The id of the comment to delete.

    Returns:
        None: Responds with 204 No Content on success.

    Raises:
        HTTPException: 404 with detail "Task not found" if no task with
            ``task_id`` exists.
        HTTPException: 404 with detail "Comment not found" if
            ``comment_id`` does not exist or does not belong to
            ``task_id``.
    """
    if storage.get_task_by_id(task_id) is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if storage.delete_comment(task_id, comment_id):
        return None
    raise HTTPException(status_code=404, detail="Comment not found")