from __future__ import annotations
from enum import Enum
from datetime import datetime
from typing import Literal, List, Union, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    TODO        = "todo"
    IN_PROGRESS = "in_progress"
    DONE        = "done"
    CANCELLED   = "cancelled"



# ─────────────────────────────────────────────────────────────────────────────
#  Pydantic-модели для structured output — именно то, что LLM возвращает
# ─────────────────────────────────────────────────────────────────────────────
class CreateTaskAction(BaseModel):
    action: Literal["create_task"]
    description: str
    dod: str
    deadline: datetime = None
    assignee: str = None

class AddSubtaskAction(BaseModel):
    action: Literal["add_subtask"]
    parent_id: str
    description: str
    dod: str
    deadline: datetime = None
    assignee: str = None

class UpdateTaskAction(BaseModel):
    action: Literal["update_task"]
    task_id: str
    new_description: Optional[str] = None
    new_dod: Optional[str] = None

class CloseTaskAction(BaseModel):
    action: Literal["close_task"]
    task_id: str
    status: Literal["done", "cancelled"]
    reason: Optional[str] = None

class DeleteTaskAction(BaseModel):
    action: Literal["delete_task"]
    task_id: str

class GetTaskAction(BaseModel):
    action: Literal["get_task"]
    task_id: str

class ListTasksAction(BaseModel):
    action: Literal["list_tasks"]
    # никаких дополнительных полей

class FinishAction(BaseModel):
    action: Literal["finish"]
    result_message: str

class SearchDuplicates(BaseModel):
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

class NextAction(BaseModel):
    reasoning: str
    action: ActionRequest

class Duplicates(BaseModel):
    reasoning: str
    is_duplicate: bool
    similar_tasks: List[str]
