from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, List, Union, Optional

from pydantic import BaseModel


class TaskStatus(str, Enum):
    """
    Enum representing the status of a task.
    """
    TODO        = "todo"
    IN_PROGRESS = "in_progress"
    DONE        = "done"
    CANCELLED   = "cancelled"



# ─────────────────────────────────────────────────────────────────────────────
#  Pydantic-модели для structured output — именно то, что LLM возвращает
# ─────────────────────────────────────────────────────────────────────────────
class CreateTaskAction(BaseModel):
    """
    Action for creating a new task.
    """
    action: Literal["create_task"]
    description: str
    dod: str
    deadline: datetime = None
    assignee: str = None

class AddSubtaskAction(BaseModel):
    """
    Action for adding a subtask to an existing task.
    """
    action: Literal["add_subtask"]
    parent_id: str
    description: str
    dod: str
    deadline: datetime = None
    assignee: str = None

class UpdateTaskAction(BaseModel):
    """
    Action for updating an existing task.
    """
    action: Literal["update_task"]
    task_id: str
    new_description: Optional[str] = None
    new_dod: Optional[str] = None

class CloseTaskAction(BaseModel):
    """
    Action for closing a task (done or cancelled).
    """
    action: Literal["close_task"]
    task_id: str
    status: Literal["done", "cancelled"]
    reason: Optional[str] = None

class DeleteTaskAction(BaseModel):
    """
    Action for deleting a task.
    """
    action: Literal["delete_task"]
    task_id: str

class GetTaskAction(BaseModel):
    """
    Action for retrieving a task by its ID.
    """
    action: Literal["get_task"]
    task_id: str

class ListTasksAction(BaseModel):
    """
    Action for listing all tasks.
    """
    action: Literal["list_tasks"]

class FinishAction(BaseModel):
    """
    Action for finishing the workflow with a result message.
    """
    action: Literal["finish"]
    result_message: str

class SearchDuplicates(BaseModel):
    """
    Action for fuzzy searching for duplicate tasks.
    """
    action: Literal["fuzzy_search"]
    query: str

# ─────────────────────────────────────────────────────────────────────────────
#  Общая схема — Union всех возможных действий
# ─────────────────────────────────────────────────────────────────────────────
ActionRequest = Union[
    CreateTaskAction,
    AddSubtaskAction,
    UpdateTaskAction,
    CloseTaskAction,
    DeleteTaskAction,
    GetTaskAction,
    ListTasksAction,
    FinishAction,
]
"""
Type alias for all possible action requests that can be sent to the system.
"""

class NextAction(BaseModel):
    """
    Model representing the next action to be taken, with reasoning and action details.
    """
    reasoning: str
    action: ActionRequest

class Duplicates(BaseModel):
    """
    Model representing the result of a duplicate search.
    """
    reasoning: str
    is_duplicate: bool
    similar_tasks: List[str]
