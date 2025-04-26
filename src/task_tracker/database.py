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

class MongoDatabase(BaseDatabase):
    def __init__(self, mongodb_url: str, db_name: str):
        self.client = AsyncIOMotorClient(mongodb_url)
        self.db = self.client[db_name]
        self.trees = self.db.trees

    async def create_tree(self, name: str) -> str:
        logger.info(f"Creating tree with name: {name}")
        root_task = Task(description=name, dod="Root", status=TaskStatus.TODO)
        tree = TaskTree(root_task)
        doc = {"name": name, "tree": tree.to_dict()}
        result = await self.trees.insert_one(doc)
        logger.info(f"Tree created with ID: {result.inserted_id}")
        return str(result.inserted_id)

    async def delete_tree(self, tree_id: str) -> None:
        res = await self.trees.delete_one({"_id": ObjectId(tree_id)})
        if res.deleted_count == 0:
            logger.error(f"Tree {tree_id} not found for deletion")
            raise KeyError(f"Tree {tree_id} not found")
        logger.info(f"Tree with ID: {tree_id} deleted")

    async def list_trees(self) -> list[dict]:
        cursor = self.trees.find({}, {"_id": 1, "name": 1})
        return [{"id": str(doc["_id"]), "name": doc["name"]} async for doc in cursor]

    async def _load_tree(self, tree_id: str) -> TaskTree:
        doc = await self.trees.find_one({"_id": ObjectId(tree_id)})
        if not doc:
            logger.error(f"Tree {tree_id} not found for _load_tree")
            raise KeyError(f"Tree {tree_id} not found")
        return TaskTree.from_dict(doc["tree"])

    async def _save_tree(self, tree_id: str, tree: TaskTree):
        res = await self.trees.update_one({"_id": ObjectId(tree_id)}, {"$set": {"tree": tree.to_dict()}})
        if res.matched_count == 0:
            logger.error(f"Tree {tree_id} not found for _save_tree")
            raise KeyError(f"Tree {tree_id} not found")

    async def create_task(self, tree_id: str, parent_id: str, description: str, dod: str, **kwargs) -> str:
        tree = await self._load_tree(tree_id)
        parent = tree.get(parent_id)
        if not parent:
            logger.error(f"Parent task {parent_id} not found in tree {tree_id}")
            raise KeyError(f"Parent task {parent_id} not found in tree {tree_id}")
        task = tree.add_subtask(parent_id, description, dod, kwargs.get("deadline"), kwargs.get("assignee"))
        await self._save_tree(tree_id, tree)
        return task.id

    async def get_task(self, tree_id: str, task_id: str) -> dict:
        tree = await self._load_tree(tree_id)
        task = tree.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found in tree {tree_id}")
            raise KeyError(f"Task {task_id} not found in tree {tree_id}")
        return task.to_dict()

    async def update_task(self, tree_id: str, task_id: str, **kwargs) -> None:
        tree = await self._load_tree(tree_id)
        task = tree.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found in tree {tree_id} for update_task")
            raise KeyError(f"Task {task_id} not found in tree {tree_id}")
        tree.update(task_id, **kwargs)
        await self._save_tree(tree_id, tree)

    async def delete_task(self, tree_id: str, task_id: str) -> None:
        tree = await self._load_tree(tree_id)
        task = tree.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found in tree {tree_id} for delete_task")
            raise KeyError(f"Task {task_id} not found in tree {tree_id}")
        parent = task.parent
        if parent:
            parent.subtasks = [st for st in parent.subtasks if st.id != task_id]
            tree._index.pop(task_id, None)
        elif task == tree.root:
            await self.delete_tree(tree_id)
        await self._save_tree(tree_id, tree)

class TaskDatabase:
    def __init__(self):
        try:
            self.db = MongoDatabase(settings.mongodb_url, settings.mongodb_db_name)
            logger.info("Using MongoDB")
        except Exception as e:
            logger.warning(f"MongoDB connection failed: {e}. Switching to in-memory database.")
            self.db = InMemoryDatabase()  # Используем базу данных в памяти

    async def create_tree(self, name: str) -> str:
        return await self.db.create_tree(name)

    async def delete_tree(self, tree_id: str) -> None:
        await self.db.delete_tree(tree_id)

    async def list_trees(self) -> List[Dict[str, Any]]:
        return await self.db.list_trees()

    async def create_task(self, task: Task, tree_id: str) -> str:
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
        return await self.db.create_task(task_data)

    async def get_task(self, task_id: str, tree_id: str) -> Optional[Task]:
        return await self.db.get_task(tree_id, task_id)

    async def update_task(self, task: Task, tree_id: str) -> None:
        task_data = {
            "description": task.description,
            "dod": task.dod,
            "status": task.status.value,
            "close_reason": task.close_reason,
            "deadline": task.deadline,
            "assignee": task.assignee,
            "subtasks": [st.id for st in task.subtasks]
        }
        await self.db.update_task(tree_id, task.id, task_data)

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