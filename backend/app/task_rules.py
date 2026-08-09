from datetime import date

from app.models import TaskResponse, TaskStatus


def compute_is_overdue(due_date: date | None, status: TaskStatus, today: date) -> bool:
    """Determine whether a task counts as overdue.

    Args:
        due_date: The task's due date, or ``None`` if unset.
        status: The task's current status.
        today: The date to compare ``due_date`` against.

    Returns:
        bool: ``True`` if ``due_date`` is set, earlier than ``today``, and
        ``status`` is not ``TaskStatus.DONE``; ``False`` otherwise.
    """
    return due_date is not None and due_date < today and status is not TaskStatus.DONE


def build_task_response(task: TaskResponse, today: date, comment_count: int = 0) -> TaskResponse:
    """Build a response copy of a task with derived fields populated.

    Args:
        task: The stored task to base the response on.
        today: The date used to compute ``is_overdue``.
        comment_count: The comment count to attach. Defaults to 0.

    Returns:
        TaskResponse: A copy of ``task`` with ``is_overdue`` computed via
        ``compute_is_overdue`` and ``comment_count`` set to the given
        value.
    """
    return task.model_copy(
        update={
            "is_overdue": compute_is_overdue(task.due_date, task.status, today),
            "comment_count": comment_count,
        }
    )
