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
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
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
    # Dicts preserve insertion order, so this is already oldest-first and
    # fully deterministic. Deliberately not sorted by created_at: two comments
    # created in the same millisecond would tie, and the uuid ids give no
    # usable tiebreak.
    return [c for c in _comments.values() if c.task_id == task_id]


def delete_comment(task_id: str, comment_id: str) -> bool:
    comment = _comments.get(comment_id)
    if comment is not None and comment.task_id == task_id:
        del _comments[comment_id]
        return True
    return False


def count_comments_for_task(task_id: str) -> int:
    return sum(1 for c in _comments.values() if c.task_id == task_id)


def _reset() -> None:
    """Clear the in-memory store (for tests only)."""
    _tasks.clear()
    _comments.clear()