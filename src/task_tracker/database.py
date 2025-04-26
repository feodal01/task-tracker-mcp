from motor.motor_asyncio import AsyncIOMotorClient
from src.task_tracker.config import settings
from src.task_tracker.tasks import Task
from src.task_tracker.schemas import TaskStatus
from datetime import datetime, UTC
from typing import Optional, List, Dict, Any
from bson import ObjectId


class TaskDatabase:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.db = self.client[settings.mongodb_db_name]
        self.trees = self.db.trees
        self.tasks = self.db.tasks

    # Методы для работы с деревьями
    async def create_tree(self, name: str) -> str:
        """Создает новое дерево задач"""
        tree = {
            "name": name,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        }
        result = await self.trees.insert_one(tree)
        return str(result.inserted_id)

    async def delete_tree(self, tree_id: str) -> None:
        """Удаляет дерево задач и все его задачи"""
        # Сначала удаляем все задачи дерева
        await self.tasks.delete_many({"tree_id": tree_id})
        # Затем удаляем само дерево
        await self.trees.delete_one({"_id": ObjectId(tree_id)})

    async def list_trees(self) -> List[Dict[str, Any]]:
        """Возвращает список всех деревьев задач"""
        cursor = self.trees.find({}, {"_id": 1, "name": 1, "created_at": 1})
        trees = []
        async for tree in cursor:
            tree["id"] = str(tree.pop("_id"))
            trees.append(tree)
        return trees

    # Методы для работы с задачами
    async def create_task(self, task: Task, tree_id: str) -> str:
        """Создает новую задачу в дереве"""
        task_data = {
            "tree_id": tree_id,
            "description": task.description,
            "dod": task.dod,
            "status": task.status.value,
            "parent_id": task.parent.id if task.parent else None,
            "close_reason": task.close_reason,
            "deadline": task.deadline,
            "assignee": task.assignee,
            "subtasks": [st.id for st in task.subtasks]
        }
        result = await self.tasks.insert_one(task_data)
        return str(result.inserted_id)

    async def get_task(self, task_id: str, tree_id: str) -> Optional[Task]:
        """Получает задачу по ID"""
        task_data = await self.tasks.find_one({
            "_id": ObjectId(task_id),
            "tree_id": tree_id
        })
        if not task_data:
            return None
        return self._task_from_db(task_data)

    async def update_task(self, task: Task, tree_id: str) -> None:
        """Обновляет задачу"""
        task_data = {
            "description": task.description,
            "dod": task.dod,
            "status": task.status.value,
            "close_reason": task.close_reason,
            "deadline": task.deadline,
            "assignee": task.assignee,
            "subtasks": [st.id for st in task.subtasks]
        }
        await self.tasks.update_one(
            {"_id": ObjectId(task.id), "tree_id": tree_id},
            {"$set": task_data}
        )

    async def delete_task(self, task_id: str, tree_id: str) -> None:
        """Удаляет задачу"""
        await self.tasks.delete_one({
            "_id": ObjectId(task_id),
            "tree_id": tree_id
        })

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