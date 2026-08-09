from __future__ import annotations

from typing import Optional, List, Dict
from datetime import datetime, timezone
from uuid import uuid4

from app.models import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskStatus,
    TaskPriority,
    CommentCreate,
    CommentResponse,
)

# module-level in-memory storage
_tasks: Dict[str, TaskResponse] = {}
_comments: Dict[str, CommentResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and store a new task from validated input.

    Generates a new id and sets ``created_at``/``updated_at`` to the
    current UTC time. ``description`` defaults to ``""`` when the payload
    value is falsy (e.g. ``None``).

    Args:
        payload: Validated task-creation data.

    Returns:
        TaskResponse: The stored task record.
    """
    task_id = uuid4().hex
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=task_id,
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        created_at=now,
        updated_at=now,
    )
    _tasks[task_id] = task
    return task


def get_all_tasks(status=None, priority=None) -> List[TaskResponse]:
    """Return all stored tasks, optionally filtered by status and/or priority.

    Args:
        status: Optional ``TaskStatus`` (or its string value) to filter
            by. ``None`` means no status filter.
        priority: Optional ``TaskPriority`` (or its string value) to
            filter by. ``None`` means no priority filter.

    Returns:
        List[TaskResponse]: Matching tasks, in insertion order.

    Raises:
        ValueError: If ``status`` or ``priority`` is a string that does
            not match a valid enum value.
    """
    results = list(_tasks.values())
    if status is not None:
        # allow passing either enum or its value; compare to enum
        if isinstance(status, (str,)):
            status = TaskStatus(status)
        results = [t for t in results if t.status == status]
    if priority is not None:
        if isinstance(priority, (str,)):
            priority = TaskPriority(priority)
        results = [t for t in results if t.priority == priority]
    return list(results)


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Look up a task by id.

    Args:
        task_id: The task id to look up.

    Returns:
        Optional[TaskResponse]: The task if found, else ``None``.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to an existing task.

    Only fields explicitly set on ``payload`` (``exclude_unset=True``) are
    applied to a copy of the existing task; ``id`` and ``created_at`` are
    preserved, and ``updated_at`` is refreshed to the current UTC time. If
    no fields were set, the existing task is returned unchanged and
    ``updated_at`` is left untouched.

    Args:
        task_id: The id of the task to update.
        payload: Fields to change.

    Returns:
        Optional[TaskResponse]: The updated task, or ``None`` if no task
        with ``task_id`` exists.
    """
    existing = _tasks.get(task_id)
    if existing is None:
        return None

    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        return existing

    # Create an updated copy preserving created_at and id
    updated = existing.model_copy(deep=True)
    for key, value in changes.items():
        # only set known editable fields
        if key in {"title", "description", "status", "priority", "assignee", "due_date"}:
            setattr(updated, key, value)
    updated.updated_at = datetime.now(timezone.utc)
    _tasks[task_id] = updated
    return updated


def delete_task(task_id: str) -> bool:
    """Delete a task and cascade-delete all of its comments.

    Args:
        task_id: The id of the task to delete.

    Returns:
        bool: ``True`` if the task existed and was deleted, ``False``
        otherwise (in which case no comments are touched).
    """
    if task_id not in _tasks:
        return False

    del _tasks[task_id]

    # Cascade: remove every comment belonging to this task, in the same call.
    orphaned = [cid for cid, c in _comments.items() if c.task_id == task_id]
    for cid in orphaned:
        del _comments[cid]

    return True


# ---------------------------------------------------------------- comments


def add_comment(task_id: str, payload: CommentCreate) -> CommentResponse:
    """Create and store a new comment for a task.

    Does not verify that ``task_id`` refers to an existing task; callers
    (see ``main.create_comment``) are expected to check that first.

    Args:
        task_id: The id of the task to attach the comment to.
        payload: Validated comment data.

    Returns:
        CommentResponse: The stored comment record.
    """
    comment_id = uuid4().hex
    comment = CommentResponse(
        id=comment_id,
        task_id=task_id,
        text=payload.text,
        author=payload.author,
        created_at=datetime.now(timezone.utc),
    )
    _comments[comment_id] = comment
    return comment


def get_comments_for_task(task_id: str) -> List[CommentResponse]:
    """Return all comments belonging to a task, oldest first.

    Relies on dict insertion order rather than sorting by ``created_at``:
    two comments created in the same millisecond would tie, and the uuid
    ids give no usable tiebreak.

    Args:
        task_id: The id of the task whose comments to return.

    Returns:
        List[CommentResponse]: Matching comments, in insertion order.
    """
    # Dicts preserve insertion order, so this is already oldest-first and
    # fully deterministic. Deliberately not sorted by created_at: two comments
    # created in the same millisecond would tie, and the uuid ids give no
    # usable tiebreak.
    return [c for c in _comments.values() if c.task_id == task_id]


def delete_comment(task_id: str, comment_id: str) -> bool:
    """Delete a single comment, scoped to its owning task.

    Args:
        task_id: The id of the task the comment is expected to belong to.
        comment_id: The id of the comment to delete.

    Returns:
        bool: ``True`` if a comment with ``comment_id`` existed and
        belonged to ``task_id`` (and was deleted), ``False`` otherwise.
    """
    comment = _comments.get(comment_id)
    if comment is not None and comment.task_id == task_id:
        del _comments[comment_id]
        return True
    return False


def count_comments_for_task(task_id: str) -> int:
    """Count the comments belonging to a task.

    Args:
        task_id: The id of the task to count comments for.

    Returns:
        int: The number of comments whose ``task_id`` matches.
    """
    return sum(1 for c in _comments.values() if c.task_id == task_id)


def _reset() -> None:
    """Clear the in-memory store (for tests only)."""
    _tasks.clear()
    _comments.clear()