from typing import Optional, List
import json
from datetime import datetime

from src.task_tracker.tasks import Task
from src.task_tracker.schemas import TaskStatus


class TaskTree:
    """
    Менеджер дерева задач:
      • O(1) доступ к любой задаче по id   • update / close / add_subtask
      • сериализация ↔ десериализация в JSON
    """

    # ────────────────────────── init & индекс ───────────────────────── #
    def __init__(self, root: Task):
        self.root = root
        self._index: dict[str, Task] = {}
        self._rebuild_index(root)

    def _rebuild_index(self, node: Task):
        """(Пере)строить индекс целиком – вызываем при загрузке / update."""
        self._index[node.id] = node
        for st in node.subtasks:
            self._rebuild_index(st)

    # ─────────────────────────── базовое API ────────────────────────── #
    def get(self, task_id: str) -> Optional[Task]:
        """
        get task by it id
        """
        return self._index.get(task_id)

    def add_subtask(self, parent_id: str, desc: str, dod: str, deadline = None, assignee = None) -> Optional[Task]:
        """
        add subtask to specific task
        """
        parent = self.get(parent_id)
        if parent is None:
            raise KeyError(f"Parent id {parent_id} not found in tree")
        
        child = parent.add_subtask(desc, dod, deadline, assignee)
        self._index[child.id] = child
        return child

    def close(self, task_id: str, status: TaskStatus, reason: str | None = None):
        """
        close task by its id
        """
        task = self.get(task_id)
        if task:
            task.close(status, reason)

    # ───────────────────────  🔄  update по id  ─────────────────────── #
    def update(
        self,
        task_id: str,
        *,
        description: str | None = None,
        dod: str | None = None,
        status: TaskStatus | None = None,
        deadline: datetime | None = None,
        assignee: str | None = None,
        subtasks: List[tuple[str, str]] | None = None,
    ):
        """
        Обновляет параметры задачи по её ID. Все параметры опциональны.
        
        Args:
            task_id: ID задачи для обновления
            description: Новое описание задачи
            dod: Новые критерии приемки
            status: Новый статус задачи
            deadline: Новый дедлайн
            assignee: Новый исполнитель
            subtasks: Список кортежей (description, dod) для замены подзадач
        """
        task = self.get(task_id)
        if task is None:
            raise KeyError(f"Task id {task_id} not found")
        task.update(
            description=description,
            dod=dod,
            status=status,
            deadline=deadline,
            assignee=assignee,
            subtasks=subtasks,
        )
        # subtasks могли поменяться → пересобираем индекс
        self._index.clear()
        self._rebuild_index(self.root)

    # ─────────────────── JSON сериализация / I/O ────────────────────── #
    def to_dict(self) -> dict:
        """JSON-ready dict всей иерархии (корень)."""
        return self.root.to_dict()

    def to_json(self, *, indent: int | None = 2, ensure_ascii=False) -> str:
        """
        save tree to json
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=ensure_ascii)

    def save(self, path: str, *, indent: int | None = 2):
        """Сохранить дерево в файл."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json(indent=indent))

    # ------- альтернативные конструкторы (загрузка) ------------------- #
    @classmethod
    def from_json(cls, json_str: str) -> "TaskTree":
        """Создать дерево из JSON-строки."""
        data = json.loads(json_str)
        root = Task.from_dict(data)
        return cls(root)

    @classmethod
    def load(cls, path: str) -> "TaskTree":
        """
        load tree from json
        """
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_json(f.read())

    # ───────────────────────── красивая печать ──────────────────────── #
    def __str__(self) -> str:
        return str(self.root)
