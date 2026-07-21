from __future__ import annotations

from typing import Optional, List, Dict
from datetime import datetime, timezone
from uuid import uuid4

from app.models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority

# module-level in-memory storage
_tasks: Dict[str, TaskResponse] = {}


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
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def _reset() -> None:
    """Clear the in-memory store (for tests only)."""
    _tasks.clear()
