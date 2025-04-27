import logging
from datetime import datetime

from mcp.server.fastmcp import FastMCP

from task_tracker.database import InMemoryDatabase
from task_tracker.schemas import TaskStatus

MCP_SERVER_NAME = "task-tracker-mcp"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='mcp_server.log',
    filemode='a'
)
logger = logging.getLogger(MCP_SERVER_NAME)

# Инициализируем MCP сервер
mcp = FastMCP(MCP_SERVER_NAME)

db = InMemoryDatabase()

@mcp.tool()
async def create_task(
        description: str,
        dod: str,
        deadline: datetime | None = None,
        assignee: str | None = None,
        parent_id: str | None = None
) -> str:
    """Creates a new task (or subtask) in the single task tree.
    Args:
        description: Task description
        dod: Definition of Done
        deadline: Deadline (optional)
        assignee: Assignee (optional)
        parent_id: Parent task ID (if not specified, will be added to the root)
    """
    parent_id = parent_id or db.tree.root.id
    task_id = await db.create_task(parent_id, description, dod, deadline=deadline, assignee=assignee)
    return f"Task created with ID: {task_id}"

@mcp.tool()
async def update_task(
    task_id: str,
    description: str | None = None,
    dod: str | None = None,
    status: TaskStatus | None = None,
    close_reason: str | None = None,
    deadline: str | None = None,
    assignee: str | None = None,
) -> str:
    """
    Updates an existing task. You can update any of the following fields:

    Args:
        task_id (str): ID of the task to update.
        description (str, optional): New description for the task.
        dod (str, optional): New Definition of Done for the task.
        status (str, optional): New status for the task (todo, in_progress, done, cancelled).
        close_reason (str, optional): Reason for closing the task (if applicable).
        deadline (str, optional): New deadline for the task.
        assignee (str, optional): New assignee for the task.

    Any combination of these fields can be provided. Only non-null values will be updated.
    """
    task = await db.get_task(task_id)
    if not task:
        return f"Task with ID {task_id} not found"

    # Преобразуем статус к Enum, если передан
    status_enum = TaskStatus(status) if status else None

    await db.update_task(
        task_id,
        description=description,
        dod=dod,
        status=status_enum,
        close_reason=close_reason,
        deadline=deadline,
        assignee=assignee,
    )
    return f"Task {task_id} updated"

@mcp.tool()
async def close_task(
        task_id: str,
        status: str,
        reason: str | None = None
) -> str:
    """Closes a task.
    Args:
        task_id: Task ID
        status: Status (done/cancelled)
        reason: Close reason (optional)
    """
    await db.update_task(
        task_id,
        status=TaskStatus(status),
        close_reason=reason
    )
    return f"Task {task_id} closed"

@mcp.tool()
async def delete_task(task_id: str) -> str:
    """Deletes a task.
    Args:
        task_id: Task ID
    """
    await db.delete_task(task_id)
    return f"Task {task_id} deleted"

@mcp.tool()
async def get_task(task_id: str) -> str:
    """Retrieves information about a task.
    Args:
        task_id: Task ID
    """
    task = await db.get_task(task_id)
    if not task:
        return f"Task with ID {task_id} not found"
    return str(task)

@mcp.tool()
async def test_tool() -> str:
    """Test function for checking MCP server health."""
    return "Test function is working"

@mcp.tool()
async def list_tasks() -> str:
    """Returns a list of all tasks in the tree (including subtasks)."""
    return str(db.tree)

if __name__ == "__main__":
    mcp.run(transport='stdio')