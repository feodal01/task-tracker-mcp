import json
from datetime import datetime
from typing import Optional, List

from task_tracker.schemas import TaskStatus
from task_tracker.tasks import Task


class TaskTree:
    """
    TaskTree manages a hierarchy of tasks with O(1) access by id, supports update/close/add_subtask,
    and provides serialization/deserialization to and from JSON.
    """

    # ────────────────────────── init & индекс ───────────────────────── #
    def __init__(self, root: Task):
        """
        Initialize the task tree with a root task.

        Args:
            root (Task): The root task of the tree.
        """
        self.root = root
        self._index: dict[str, Task] = {}
        self._rebuild_index(root)

    def _rebuild_index(self, node: Task):
        """
        (Re)build the index for fast access to tasks by id. Called on load or update.
        """
        self._index[node.id] = node
        for st in node.subtasks:
            self._rebuild_index(st)

    # ─────────────────────────── базовое API ────────────────────────── #
    def get(self, task_id: str) -> Optional[Task]:
        """
        Get a task by its id.

        Args:
            task_id (str): The id of the task to retrieve.

        Returns:
            Task or None: The found task, or None if not found.
        """
        return self._index.get(task_id)

    def add_subtask(
        self, parent_id: str, desc: str, dod: str, deadline=None, assignee=None
    ) -> Optional[Task]:
        """
        Add a subtask to a specific parent task.

        Args:
            parent_id (str): The id of the parent task.
            desc (str): Description of the subtask.
            dod (str): Definition of Done for the subtask.
            deadline (optional): Deadline for the subtask.
            assignee (optional): Assignee for the subtask.

        Returns:
            Task: The created subtask.

        Raises:
            KeyError: If the parent task is not found.
        """
        parent = self.get(parent_id)
        if parent is None:
            raise KeyError(f"Parent id {parent_id} not found in tree")
        child = parent.add_subtask(desc, dod, deadline, assignee)
        self._index[child.id] = child
        return child

    def close(self, task_id: str, status: TaskStatus, reason: str | None = None):
        """
        Close a task by its id.

        Args:
            task_id (str): The id of the task to close.
            status (TaskStatus): The new status (DONE or CANCELLED).
            reason (str, optional): Reason for closing the task.
        """
        task = self.get(task_id)
        if task:
            task.close(status, reason)

    # ───────────────────────  🔄  update по id  ─────────────────────── #
    def update(self, task_id: str, **kwargs):
        """
        Update task parameters by its ID. All parameters are optional and passed as keyword arguments.
        Any field present in the Task can be updated.

        Args:
            task_id (str): ID of the task to update.
            **kwargs: Fields to update.

        Raises:
            KeyError: If the task is not found.
        """
        task = self.get(task_id)
        if task is None:
            raise KeyError(f"Task id {task_id} not found")
        task.update(**kwargs)
        self._index.clear()
        self._rebuild_index(self.root)

    # ─────────────────── JSON сериализация / I/O ────────────────────── #
    def to_dict(self) -> dict:
        """
        Get a JSON-ready dict of the entire hierarchy (root).

        Returns:
            dict: Dictionary representation of the tree.
        """
        return self.root.to_dict()

    def to_json(self, *, indent: int | None = 2, ensure_ascii=False) -> str:
        """
        Serialize the tree to a JSON string.

        Args:
            indent (int, optional): Indentation for pretty-printing.
            ensure_ascii (bool): Whether to escape non-ASCII characters.

        Returns:
            str: JSON string of the tree.
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=ensure_ascii)

    def save(self, path: str, *, indent: int | None = 2):
        """
        Save the tree to a file in JSON format.

        Args:
            path (str): Path to the file.
            indent (int, optional): Indentation for pretty-printing.
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json(indent=indent))

    # ------- альтернативные конструкторы (загрузка) ------------------- #
    @classmethod
    def from_json(cls, json_str: str) -> "TaskTree":
        """
        Create a tree from a JSON string.

        Args:
            json_str (str): JSON string with tree data.

        Returns:
            TaskTree: The deserialized tree.
        """
        data = json.loads(json_str)
        root = Task.from_dict(data)
        return cls(root)

    @classmethod
    def load(cls, path: str) -> "TaskTree":
        """
        Load a tree from a JSON file.

        Args:
            path (str): Path to the file.

        Returns:
            TaskTree: The loaded tree.
        """
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_json(f.read())

    @classmethod
    def from_dict(cls, data: dict) -> "TaskTree":
        """
        Create a tree from a dictionary.

        Args:
            data (dict): Dictionary with tree data.

        Returns:
            TaskTree: The deserialized tree.
        """
        root = Task.from_dict(data)
        return cls(root)

    # ───────────────────────── красивая печать ──────────────────────── #
    def __str__(self) -> str:
        """
        Return a pretty-printed string representation of the tree.

        Returns:
            str: Multiline string with the tree structure.
        """
        return str(self.root)
