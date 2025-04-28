import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from task_tracker.schemas import TaskStatus
from task_tracker.tasks import Task
from task_tracker.tree import TaskTree

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BaseDatabase(ABC):
    """
    Abstract base class for a task database interface.
    """

    @abstractmethod
    async def create_task(
        self, parent_id: str, description: str, dod: str, **kwargs
    ) -> str:
        """
        Create a new task in the specified tree.
        """
        pass

    @abstractmethod
    async def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Retrieve a task by its ID from the specified tree.
        """
        pass

    @abstractmethod
    async def update_task(self, task_id: str, **kwargs) -> None:
        """
        Update a task in the specified tree.
        """
        pass

    @abstractmethod
    async def delete_task(self, task_id: str) -> None:
        """
        Delete a task from the specified tree.
        """
        pass


class InMemoryDatabase(BaseDatabase):
    """
    In-memory implementation of the task database. Stores all tasks in a single tree.
    """

    def __init__(self):
        """
        Initialize the in-memory database with a single root task tree.
        """
        root_task = Task(description="Main", dod="Root", status=TaskStatus.TODO)
        self.tree = TaskTree(root_task)

    async def create_task(
        self, parent_id: str, description: str, dod: str, **kwargs
    ) -> str:
        """
        Create a new subtask under the specified parent task.

        Args:
            parent_id (str): ID of the parent task.
            description (str): Task description.
            dod (str): Definition of Done.
            deadline (optional): Task deadline.
            assignee (optional): Task assignee.

        Returns:
            str: ID of the created task.

        Raises:
            KeyError: If the parent task is not found.
        """
        await asyncio.sleep(0)
        parent = self.tree.get(parent_id)
        if not parent:
            logger.error(f"Parent task {parent_id} not found in tree")
            raise KeyError(f"Parent task {parent_id} not found in tree")
        task = self.tree.add_subtask(
            parent_id, description, dod, kwargs.get("deadline"), kwargs.get("assignee")
        )
        logger.info(f"Task {task.id} created under parent {parent_id}: {description}")
        return task.id

    async def get_task(self, task_id: str) -> dict:
        """
        Retrieve a task by its ID.

        Args:
            task_id (str): ID of the task to retrieve.

        Returns:
            dict: Task data as a dictionary.

        Raises:
            KeyError: If the task is not found.
        """
        await asyncio.sleep(0)
        task = self.tree.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found in tree")
            raise KeyError(f"Task {task_id} not found in tree")
        logger.info(f"Task {task_id} retrieved")
        return task.to_dict()

    async def update_task(self, task_id: str, **kwargs) -> None:
        """
        Update a task by its ID.

        Args:
            task_id (str): ID of the task to update.
            **kwargs: Fields to update (description, dod, status, deadline, assignee, subtasks, etc).

        Raises:
            KeyError: If the task is not found.
        """
        await asyncio.sleep(0)
        task = self.tree.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found in tree for update_task")
            raise KeyError(f"Task {task_id} not found in tree")
        # Convert status to Enum if passed as string
        if "status" in kwargs and isinstance(kwargs["status"], str):
            from task_tracker.schemas import TaskStatus

            kwargs["status"] = TaskStatus(kwargs["status"])
        self.tree.update(task_id, **kwargs)
        logger.info(f"Task {task_id} updated with {kwargs}")

    async def delete_task(self, task_id: str) -> None:
        """
        Delete a task by its ID. Cannot delete the root task.

        Args:
            task_id (str): ID of the task to delete.

        Raises:
            KeyError: If the task is not found.
            Exception: If attempting to delete the root task.
        """
        await asyncio.sleep(0)
        task = self.tree.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found in tree for delete_task")
            raise KeyError(f"Task {task_id} not found in tree")
        parent = task.parent
        if parent:
            parent.subtasks = [st for st in parent.subtasks if st.id != task_id]
            self.tree._index.pop(task_id, None)
            logger.info(f"Task {task_id} deleted from parent {parent.id}")
        elif task == self.tree.root:
            logger.warning("Attempt to delete root task was blocked")
            raise Exception("Cannot delete the root task")
