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
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = None,
) -> list[TaskResponse]:
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
    today = date.today()
    task = storage.add_task(payload)
    return build_task_response(
        task, today=today, comment_count=storage.count_comments_for_task(task.id)
    )


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    today = date.today()
    task = storage.get_task_by_id(task_id)
    if task is not None:
        return build_task_response(
            task, today=today, comment_count=storage.count_comments_for_task(task_id)
        )
    raise HTTPException(status_code=404, detail="Task not found")


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
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
    if storage.get_task_by_id(task_id) is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return storage.add_comment(task_id, payload)


@app.get(
    "/tasks/{task_id}/comments",
    response_model=list[CommentResponse],
    tags=["comments"],
)
def list_comments(task_id: str) -> list[CommentResponse]:
    if storage.get_task_by_id(task_id) is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return storage.get_comments_for_task(task_id)


@app.delete(
    "/tasks/{task_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["comments"],
)
def delete_comment(task_id: str, comment_id: str) -> None:
    if storage.get_task_by_id(task_id) is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if storage.delete_comment(task_id, comment_id):
        return None
    raise HTTPException(status_code=404, detail="Comment not found")