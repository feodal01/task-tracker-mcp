from motor.motor_asyncio import AsyncIOMotorClient
from task_tracker.config import settings
from task_tracker.tasks import Task
from task_tracker.schemas import TaskStatus
from typing import Optional, List, Dict, Any
from bson import ObjectId
import logging
from abc import ABC, abstractmethod
from task_tracker.tree import TaskTree
import asyncio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseDatabase(ABC):
    @abstractmethod
    async def create_tree(self, name: str) -> str:
        pass

    @abstractmethod
    async def delete_tree(self, tree_id: str) -> None:
        pass

    @abstractmethod
    async def list_trees(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def create_task(self, tree_id: str, parent_id: str, description: str, dod: str, **kwargs) -> str:
        pass

    @abstractmethod
    async def get_task(self, tree_id: str, task_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def update_task(self, tree_id: str, task_id: str, task_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def delete_task(self, tree_id: str, task_id: str) -> None:
        pass

class InMemoryDatabase(BaseDatabase):
    def __init__(self):
        self.trees = {}
        self.tree_counter = 0

    async def create_tree(self, name: str) -> str:
        await asyncio.sleep(0)
        self.tree_counter += 1
        tree_id = str(self.tree_counter)
        root_task = Task(description=name, dod="Root", status=TaskStatus.TODO)
        self.trees[tree_id] = TaskTree(root_task)
        return tree_id

    async def delete_tree(self, tree_id: str) -> None:
        await asyncio.sleep(0)
        if tree_id not in self.trees:
            logger.error(f"Tree {tree_id} not found for deletion")
            raise KeyError(f"Tree {tree_id} not found")
        self.trees.pop(tree_id)

    async def list_trees(self) -> list[dict]:
        await asyncio.sleep(0)
        return [{"id": tid, "name": tree.root.description} for tid, tree in self.trees.items()]

    async def create_task(self, tree_id: str, parent_id: str, description: str, dod: str, **kwargs) -> str:
        await asyncio.sleep(0)
        if tree_id not in self.trees:
            logger.error(f"Tree {tree_id} not found for create_task")
            raise KeyError(f"Tree {tree_id} not found")
        tree = self.trees[tree_id]
        parent = tree.get(parent_id)
        if not parent:
            logger.error(f"Parent task {parent_id} not found in tree {tree_id}")
            raise KeyError(f"Parent task {parent_id} not found in tree {tree_id}")
        task = tree.add_subtask(parent_id, description, dod, kwargs.get("deadline"), kwargs.get("assignee"))
        return task.id

    async def get_task(self, tree_id: str, task_id: str) -> dict:
        await asyncio.sleep(0)
        if tree_id not in self.trees:
            logger.error(f"Tree {tree_id} not found for get_task")
            raise KeyError(f"Tree {tree_id} not found")
        tree = self.trees[tree_id]
        task = tree.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found in tree {tree_id}")
            raise KeyError(f"Task {task_id} not found in tree {tree_id}")
        return task.to_dict()

    async def update_task(self, tree_id: str, task_id: str, **kwargs) -> None:
        await asyncio.sleep(0)
        if tree_id not in self.trees:
            logger.error(f"Tree {tree_id} not found for update_task")
            raise KeyError(f"Tree {tree_id} not found")
        tree = self.trees[tree_id]
        task = tree.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found in tree {tree_id} for update_task")
            raise KeyError(f"Task {task_id} not found in tree {tree_id}")
        tree.update(task_id, **kwargs)

    async def delete_task(self, tree_id: str, task_id: str) -> None:
        await asyncio.sleep(0)
        if tree_id not in self.trees:
            logger.error(f"Tree {tree_id} not found for delete_task")
            raise KeyError(f"Tree {tree_id} not found")
        tree = self.trees[tree_id]
        task = tree.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found in tree {tree_id} for delete_task")
            raise KeyError(f"Task {task_id} not found in tree {tree_id}")
        parent = task.parent
        if parent:
            parent.subtasks = [st for st in parent.subtasks if st.id != task_id]
            tree._index.pop(task_id, None)
        elif task == tree.root:
            self.trees.pop(tree_id)

class TaskDatabase:
    def __init__(self):
        self.db = InMemoryDatabase()

    async def create_tree(self, name: str) -> str:
        return await self.db.create_tree(name)

    async def delete_tree(self, tree_id: str) -> None:
        await self.db.delete_tree(tree_id)

    async def list_trees(self) -> List[Dict[str, Any]]:
        return await self.db.list_trees()

    async def create_task(self, task: Task, tree_id: str) -> str:
        # Для in-memory parent_id обязателен, поэтому берём id корня, если нет parent
        parent_id = task.parent.id if task.parent else self.db.trees[tree_id].root.id
        return await self.db.create_task(
            tree_id, parent_id, task.description, task.dod,
            deadline=task.deadline, assignee=task.assignee
        )

    async def get_task(self, task_id: str, tree_id: str) -> Optional[Task]:
        data = await self.db.get_task(tree_id, task_id)
        if data is None:
            return None
        return Task.from_dict(data)

    async def update_task(self, task: Task, tree_id: str) -> None:
        await self.db.update_task(
            tree_id, task.id,
            description=task.description,
            dod=task.dod,
            status=task.status.value,
            close_reason=task.close_reason,
            deadline=task.deadline,
            assignee=task.assignee,
            subtasks=[(st.description, st.dod) for st in task.subtasks]
        )

    async def delete_task(self, task_id: str, tree_id: str) -> None:
        await self.db.delete_task(tree_id, task_id)

    async def get_subtasks(self, parent_id: str, tree_id: str) -> List[Task]:
        """Получает подзадачи"""
        cursor = self.tasks.find({
            "parent_id": parent_id,
            "tree_id": tree_id
        })
        tasks = []
        async for task_data in cursor:
            tasks.append(self._task_from_db(task_data))
        return tasks

    @staticmethod
    def _task_from_db(data: dict) -> Task:
        """Преобразует данные из БД в объект Task"""
        task = Task(
            description=data["description"],
            dod=data["dod"],
            status=TaskStatus(data["status"]),
            id=str(data["_id"]),
            close_reason=data.get("close_reason"),
            deadline=data.get("deadline"),
            assignee=data.get("assignee")
        )
        return task 