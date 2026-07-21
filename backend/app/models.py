from __future__ import annotations

from enum import Enum
from typing import Optional
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[date] = None

    @field_validator("due_date", mode="before")
    @classmethod
    def _normalize_due_date(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        if isinstance(v, bool):
            raise ValueError("due_date must be a valid date")
        if isinstance(v, int):
            raise ValueError("due_date must be a valid date")
        return v

    @field_validator("title")
    @classmethod
    def _validate_title(cls, v: str) -> str:
        if v is None:
            raise ValueError("Title is required and cannot be blank")
        v = v.strip()
        if not v:
            raise ValueError("Title is required and cannot be blank")
        if len(v) > 200:
            raise ValueError("Title must not exceed 200 characters")
        return v


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None

    @field_validator("due_date", mode="before")
    @classmethod
    def _normalize_due_date(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        if isinstance(v, bool):
            raise ValueError("due_date must be a valid date")
        if isinstance(v, int):
            raise ValueError("due_date must be a valid date")
        return v

    @field_validator("title")
    @classmethod
    def _validate_title_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("Title is required and cannot be blank")
        if len(v) > 200:
            raise ValueError("Title must not exceed 200 characters")
        return v


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    due_date: Optional[date] = None
    is_overdue: bool = False
    created_at: datetime
    updated_at: datetime
