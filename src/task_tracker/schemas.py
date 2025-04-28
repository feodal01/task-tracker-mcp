from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """
    Enum representing the status of a task.
    """

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class CreateTaskParams(BaseModel):
    description: str = Field(..., description="Task description")
    dod: str = Field(..., description="Definition of Done for the task")
    deadline: datetime = Field(None, description="Task deadline (ISO8601 datetime)")
    assignee: str = Field(None, description="Assignee of the task")
    parent_id: str = Field(None, description="Parent task ID (for subtasks)")


class UpdateTaskParams(BaseModel):
    task_id: str = Field(..., description="ID of the task to update")
    description: str = Field(None, description="New description for the task")
    dod: Optional[str] = Field(None, description="New Definition of Done for the task")
    deadline: Optional[datetime] = Field(
        None, description="New deadline for the task (ISO8601 datetime)"
    )
    assignee: Optional[str] = Field(None, description="New assignee for the task")


class UpdateStatusParams(BaseModel):
    task_id: str = Field(..., description="ID of the task to update status")
    status: Literal["todo", "in_progress", "done", "cancelled"] = Field(
        ..., description="New status for the task"
    )
    reason: Optional[str] = Field(
        None, description="Reason for status change (optional)"
    )


class CloseTaskParams(BaseModel):
    task_id: str = Field(..., description="ID of the task to close")
    status: Literal["done", "cancelled"] = Field(
        ..., description="Status to set for the task (done or cancelled)"
    )
    reason: Optional[str] = Field(None, description="Reason for closing the task")


class DeleteTaskParams(BaseModel):
    task_id: str = Field(..., description="ID of the task to delete")


class GetTaskParams(BaseModel):
    task_id: str = Field(..., description="ID of the task to retrieve")
