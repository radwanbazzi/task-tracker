from datetime import date

from app.models import TaskResponse, TaskStatus


def compute_is_overdue(due_date: date | None, status: TaskStatus, today: date) -> bool:
    return due_date is not None and due_date < today and status is not TaskStatus.DONE


def build_task_response(task: TaskResponse, today: date, comment_count: int = 0) -> TaskResponse:
    return task.model_copy(
        update={
            "is_overdue": compute_is_overdue(task.due_date, task.status, today),
            "comment_count": comment_count,
        }
    )
