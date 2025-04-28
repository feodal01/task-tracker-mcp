from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from task_tracker.schemas import TaskStatus


@dataclass
class Task:
    """
    Represents a task in the task tree, supporting subtasks, status, deadlines, assignee, and serialization.
    """

    description: str
    dod: str
    status: TaskStatus = TaskStatus.TODO
    id: str = field(default_factory=lambda: str(uuid4()))
    parent: Optional["Task"] = field(default=None, repr=False)
    subtasks: List["Task"] = field(default_factory=list, repr=False)
    close_reason: Optional[str] = None
    deadline: datetime | None = None
    assignee: str | None = None

    # ------------------------------------------------------------------ #
    #  💬  Работа c деревом
    # ------------------------------------------------------------------ #
    def add_subtask(
        self,
        description: str,
        dod: str,
        deadline: datetime | None = None,
        assignee: str | None = None,
    ) -> "Task":
        """
        Add a subtask to this task.

        Args:
            description (str): Subtask description.
            dod (str): Definition of Done for the subtask.
            deadline (datetime, optional): Subtask deadline.
            assignee (str, optional): Subtask assignee.

        Returns:
            Task: The created subtask.
        """
        child = Task(
            description, dod, parent=self, deadline=deadline, assignee=assignee
        )
        self.subtasks.append(child)
        return child

    def find(self, task_id: str) -> Optional["Task"]:
        """
        Recursively search for a task by its ID in the subtree rooted at this task.

        Args:
            task_id (str): ID of the task to find.

        Returns:
            Task or None: The found task, or None if not found.
        """
        if self.id == task_id:
            return self
        for st in self.subtasks:
            found = st.find(task_id)
            if found:
                return found
        return None

    # ------------------------------------------------------------------ #
    #  ✅  Завершение / отмена
    # ------------------------------------------------------------------ #
    def close(self, status: TaskStatus, reason: str | None = None) -> None:
        """
        Close the task (set status to DONE or CANCELLED) with an optional reason.

        Args:
            status (TaskStatus): New status (must be DONE or CANCELLED).
            reason (str, optional): Reason for closing the task.

        Raises:
            ValueError: If status is not DONE or CANCELLED.
        """
        if status not in (TaskStatus.DONE, TaskStatus.CANCELLED):
            raise ValueError("Only DONE or CANCELLED are allowed for close")
        self.status = status
        self.close_reason = reason

    # ------------------------------------------------------------------ #
    #  🔄  Update
    # ------------------------------------------------------------------ #
    def update(self, **kwargs) -> None:
        """
        Update task parameters dynamically. Any field present in the Task can be updated by passing it as a keyword argument.
        Only non-None values will be set.

        Example:
            task.update(description="New desc", status=TaskStatus.DONE)
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)

    # ------------------------------------------------------------------ #
    #  🗄  Сериализация
    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict:
        """
        Serialize the task and its subtasks to a dictionary.

        Returns:
            dict: Dictionary representation of the task.
        """
        return {
            "id": self.id,
            "description": self.description,
            "dod": self.dod,
            "status": self.status.value,
            "close_reason": self.close_reason,
            "subtasks": [st.to_dict() for st in self.subtasks],
            "deadline": self.deadline,
            "assignee": self.assignee,
        }

    @staticmethod
    def from_dict(data: dict, parent: "Task" = None) -> "Task":
        """
        Deserialize a task (and its subtasks) from a dictionary.

        Args:
            data (dict): Dictionary with task data.
            parent (Task, optional): Parent task.

        Returns:
            Task: The deserialized task.
        """
        task = Task(
            description=data["description"],
            dod=data["dod"],
            status=TaskStatus(data["status"]),
            id=data["id"],
            parent=parent,
            close_reason=data.get("close_reason"),
            deadline=data.get("deadline"),
            assignee=data.get("assignee"),
        )
        task.subtasks = [
            Task.from_dict(sd, parent=task) for sd in data.get("subtasks", [])
        ]
        return task

    # ------------------------------------------------------------------ #
    #  👁  Удобный вывод
    # ------------------------------------------------------------------ #
    def __str__(self, level: int = 0) -> str:
        """
        Return a pretty-printed string representation of the task and its subtasks.

        Args:
            level (int): Indentation level (used for recursion).

        Returns:
            str: Multiline string with the task tree.
        """
        indent = "  " * level
        reason = f" • {self.close_reason}" if self.close_reason else ""
        head = f"{indent}- [{self.status.value}] {self.description} (id={self.id})"
        head += f" – DoD: {self.dod}{reason}"
        head += f" – Deadline: {self.deadline}"
        head += f" – Assignee: {self.assignee}"
        head += f" – Status: {self.status}"
        head += f" – Close reason: {self.close_reason}"
        lines = [head]
        for st in self.subtasks:
            lines.append(st.__str__(level + 1))
        return "\n".join(lines)
