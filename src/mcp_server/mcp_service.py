import logging

from mcp.server.fastmcp import FastMCP

from task_tracker.database import InMemoryDatabase
from task_tracker.schemas import TaskStatus
from task_tracker.tasks import Task

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
async def create_task(description: str, dod: str, deadline: str | None = None, assignee: str | None = None, parent_id: str | None = None) -> str:
    """Creates a new task (or subtask) in the single task tree.
    Args:
        description: Task description
        dod: Definition of Done
        deadline: Deadline (optional)
        assignee: Assignee (optional)
        parent_id: Parent task ID (if not specified, will be added to the root)
    """
    task = Task(
        description=description,
        dod=dod,
        deadline=deadline,
        assignee=assignee
    )
    if parent_id:
        parent = await db.get_task(parent_id)
        if not parent:
            return f"Parent task with ID {parent_id} not found"
        task.parent = parent
    await db.create_task(task)
    return f"Task created with ID: {task.id}"

@mcp.tool()
async def update_task(task_id: str, description: str | None = None, dod: str | None = None) -> str:
    """Updates an existing task.
    Args:
        task_id: Task ID
        description: New description (optional)
        dod: New Definition of Done (optional)
    """
    task = await db.get_task(task_id)
    if not task:
        return f"Task with ID {task_id} not found"
    task.update(
        description=description,
        dod=dod
    )
    await db.update_task(task)
    return f"Task {task_id} updated"

@mcp.tool()
async def close_task(task_id: str, status: str, reason: str | None = None) -> str:
    """Closes a task.
    Args:
        task_id: Task ID
        status: Status (done/cancelled)
        reason: Close reason (optional)
    """
    task = await db.get_task(task_id)
    if not task:
        return f"Task with ID {task_id} not found"
    task.close(TaskStatus(status), reason)
    await db.update_task(task)
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

if __name__ == "__main__":
    mcp.run(transport='stdio')