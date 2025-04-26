from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

from task_tracker.schemas import TaskStatus


@dataclass
class Task:
    description: str
    dod: str
    status: TaskStatus = TaskStatus.TODO
    id: str = field(default_factory=lambda: str(uuid4()))
    parent: Optional['Task'] = field(default=None, repr=False)
    subtasks: List['Task'] = field(default_factory=list, repr=False)
    close_reason: Optional[str] = None
    deadline: datetime | None = None
    assignee: str | None = None

    # ------------------------------------------------------------------ #
    #  💬  Работа c деревом
    # ------------------------------------------------------------------ #
    def add_subtask(self, description: str, dod: str, deadline: datetime | None = None, assignee: str | None = None) -> 'Task':
        child = Task(description, dod, parent=self, deadline=deadline, assignee=assignee)
        self.subtasks.append(child)
        return child

    def find(self, task_id: str) -> Optional['Task']:
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
        Закрывает задачу (DONE / CANCELLED / …) с указанием причины.

        Пример:
            task.close(TaskStatus.DONE, "фича задеплоена и протестирована")
            task.close(TaskStatus.CANCELLED, "требование устарело")
        """
        if status not in (TaskStatus.DONE, TaskStatus.CANCELLED):
            raise ValueError("При close разрешены только DONE или CANCELLED")
        self.status = status
        self.close_reason = reason

    # ------------------------------------------------------------------ #
    #  🔄  Update
    # ------------------------------------------------------------------ #
    def update(
        self,
        *,
        description: str | None = None,
        dod: str | None = None,
        status: TaskStatus | None = None,
        deadline: datetime | None = None,
        assignee: str | None = None,
        subtasks: List[tuple[str, str]] | None = None,
    ) -> None:
        """
        Обновляет параметры задачи. Все параметры опциональны.
        
        Args:
            description: Новое описание задачи
            dod: Новые критерии приемки
            status: Новый статус задачи
            deadline: Новый дедлайн
            assignee: Новый исполнитель
            subtasks: Список кортежей (description, dod) для замены подзадач
        """
        if description is not None:
            self.description = description
        if dod is not None:
            self.dod = dod
        if status is not None:
            self.status = status
        if deadline is not None:
            self.deadline = deadline
        if assignee is not None:
            self.assignee = assignee
        if subtasks is not None:
            self.subtasks.clear()
            for desc, dod in subtasks:
                self.add_subtask(desc, dod)

    # ------------------------------------------------------------------ #
    #  🗄  Сериализация
    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "dod": self.dod,
            "status": self.status.value,
            "close_reason": self.close_reason,
            "subtasks": [st.to_dict() for st in self.subtasks],
            "deadline": self.deadline,
            "assignee": self.assignee
        }

    @staticmethod
    def from_dict(data: dict, parent: 'Task' = None) -> 'Task':
        task = Task(
            description=data["description"],
            dod=data["dod"],
            status=TaskStatus(data["status"]),
            id=data["id"],
            parent=parent,
            close_reason=data.get("close_reason"),
            deadline=data.get('deadline'),
            assignee=data.get('assignee')
        )
        task.subtasks = [Task.from_dict(sd, parent=task) for sd in data.get("subtasks", [])]
        return task

    # ------------------------------------------------------------------ #
    #  👁  Удобный вывод
    # ------------------------------------------------------------------ #
    def __str__(self, level: int = 0) -> str:
        indent = "  " * level
        reason = f" • {self.close_reason}" if self.close_reason else ""
        head = f"{indent}- [{self.status.value}] {self.description} (id={self.id})"
        head += f" – DoD: {self.dod}{reason}"
        head += f" – Deadline: {self.deadline}"
        head += f" – Assignee: {self.assignee}"
        lines = [head]
        for st in self.subtasks:
            lines.append(st.__str__(level + 1))
        return "\n".join(lines)
